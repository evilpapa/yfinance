from abc import ABC, abstractmethod
import pandas as _pd
from typing import Dict, List, Optional
import warnings

from ..const import _QUERY1_URL_, _SENTINEL_
from ..data import YfData
from ..ticker import Ticker

_QUERY_URL_ = f'{_QUERY1_URL_}/v1/finance'

class Domain(ABC):
    """
    表示金融数据中领域实体的抽象基类，
    具有用于获取和解析数据的关键属性和方法。
    派生类必须实现 `_fetch_and_parse()` 方法。
    """

    def __init__(self, key: str, session=None, proxy=_SENTINEL_):
        """
        使用键、会话和代理初始化Domain对象。

        参数:
            key (str): 标识领域实体的唯一键。
            session (Optional[requests.Session]): 用于HTTP请求的会话对象。默认为None。
        """
        self._key: str = key
        self.session = session
        self._data: YfData = YfData(session=session)
        if proxy is not _SENTINEL_:
            warnings.warn("Set proxy via new config function: yf.set_config(proxy=proxy)", DeprecationWarning, stacklevel=2)
            self._data._set_proxy(proxy)

        self._name: Optional[str] = None
        self._symbol: Optional[str] = None
        self._overview: Optional[Dict] = None
        self._top_companies: Optional[_pd.DataFrame] = None
        self._research_reports: Optional[List[Dict[str, str]]] = None

    @property
    def key(self) -> str:
        """
        获取领域实体的键。

        返回:
            str: 领域实体的唯一键。
        """
        return self._key

    @property
    def name(self) -> str:
        """
        获取领域实体的名称。

        返回:
            str: 领域实体的名称。
        """
        self._ensure_fetched(self._name)
        return self._name

    @property
    def symbol(self) -> str:
        """
        获取领域实体的符号。

        返回:
            str: 表示领域实体的符号。
        """
        self._ensure_fetched(self._symbol)
        return self._symbol

    @property
    def ticker(self) -> Ticker:
        """
        根据领域实体的符号获取Ticker对象。

        返回:
            Ticker: 与领域实体关联的Ticker对象。
        """
        self._ensure_fetched(self._symbol)
        return Ticker(self._symbol)

    @property
    def overview(self) -> Dict:
        """
        获取领域实体的概览信息。

        返回:
            Dict: 包含领域实体概览的字典。
        """
        self._ensure_fetched(self._overview)
        return self._overview

    @property
    def top_companies(self) -> Optional[_pd.DataFrame]:
        """
        获取领域内的顶尖公司。

        返回:
            pandas.DataFrame: 包含领域内顶尖公司的DataFrame。
        """
        self._ensure_fetched(self._top_companies)
        return self._top_companies 

    @property
    def research_reports(self) -> List[Dict[str, str]]:
        """
        获取与领域实体相关的研究报告。

        返回:
            List[Dict[str, str]]: 研究报告列表，每个报告是一个包含元数据的字典。
        """
        self._ensure_fetched(self._research_reports)
        return self._research_reports

    def _fetch(self, query_url) -> Dict:
        """
        从给定的查询URL获取数据。

        参数:
            query_url (str): 用于数据查询的URL。

        返回:
            Dict: 请求返回的JSON响应数据。
        """
        params_dict = {"formatted": "true", "withReturns": "true", "lang": "en-US", "region": "US"}
        result = self._data.get_raw_json(query_url, params=params_dict)
        return result

    def _parse_and_assign_common(self, data) -> None:
        """
        解析并分配通用数据字段，例如名称、符号、概览和顶尖公司。

        参数:
            data (Dict): 从API接收的原始数据。
        """
        self._name = data.get('name')
        self._symbol = data.get('symbol')
        self._overview = self._parse_overview(data.get('overview', {}))
        self._top_companies = self._parse_top_companies(data.get('topCompanies', {}))
        self._research_reports = data.get('researchReports')

    def _parse_overview(self, overview) -> Dict:
        """
        解析领域实体的概览数据。

        参数:
            overview (Dict): 原始概览数据。

        返回:
            Dict: 包含已解析概览信息的字典。
        """
        return {
            "companies_count": overview.get('companiesCount', None),
            "market_cap": overview.get('marketCap', {}).get('raw', None),
            "message_board_id": overview.get('messageBoardId', None),
            "description": overview.get('description', None),
            "industries_count": overview.get('industriesCount', None),
            "market_weight": overview.get('marketWeight', {}).get('raw', None),
            "employee_count": overview.get('employeeCount', {}).get('raw', None)
        }

    def _parse_top_companies(self, top_companies) -> Optional[_pd.DataFrame]:
        """
        解析顶尖公司数据并将其转换为pandas DataFrame。

        参数:
            top_companies (Dict): 原始顶尖公司数据。

        返回:
            Optional[pandas.DataFrame]: 包含顶尖公司数据的DataFrame，如果无数据则返回None。
        """
        top_companies_column = ['symbol', 'name', 'rating', 'market weight']
        top_companies_values = [(c.get('symbol'), 
                                c.get('name'), 
                                c.get('rating'), 
                                c.get('marketWeight',{}).get('raw',None)) for c in top_companies]

        if not top_companies_values: 
            return None
        
        return _pd.DataFrame(top_companies_values, columns=top_companies_column).set_index('symbol')

    @abstractmethod
    def _fetch_and_parse(self) -> None:
        """
        用于获取和解析特定领域数据的抽象方法。
        必须由派生类实现。
        """
        raise NotImplementedError("_fetch_and_parse() needs to be implemented by children classes")

    def _ensure_fetched(self, attribute) -> None:
        """
        如果属性为None，则通过调用 `_fetch_and_parse()` 来确保获取该属性。

        参数:
            attribute: 要检查并可能获取的属性。
        """
        if attribute is None:
            self._fetch_and_parse()
