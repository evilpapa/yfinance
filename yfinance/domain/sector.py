from __future__ import print_function

import pandas as _pd
from typing import Dict, Optional
import warnings

from ..const import SECTOR_INDUSTY_MAPPING, _SENTINEL_
from ..data import YfData
from ..utils import dynamic_docstring, generate_list_table_from_dict, get_yf_logger

from .domain import Domain, _QUERY_URL_

class Sector(Domain):
    """
    表示一个金融市场板块，并允许检索与板块相关的数据，
    例如顶尖ETF、顶尖共同基金和行业数据。
    """

    def __init__(self, key, session=None, proxy=_SENTINEL_):
        """
        参数:
            key (str): 表示板块的键。
            session (requests.Session, optional): 用于发出请求的会话。默认为None。
            proxy (dict, optional): 包含请求代理设置的字典。默认为None。
        
        .. seealso::
   
            :attr:`Sector.industries <yfinance.Sector.industries>`
                板块和行业的映射
        """
        if proxy is not _SENTINEL_:
            warnings.warn("Set proxy via new config function: yf.set_config(proxy=proxy)", DeprecationWarning, stacklevel=2)
            YfData(session=session, proxy=proxy)

        super(Sector, self).__init__(key, session)
        self._query_url: str = f'{_QUERY_URL_}/sectors/{self._key}'
        self._top_etfs: Optional[Dict] = None
        self._top_mutual_funds: Optional[Dict] = None
        self._industries: Optional[_pd.DataFrame] = None

    def __repr__(self):
        """
        返回Sector对象的字符串表示形式。

        返回:
            str: 对象的字符串表示形式。
        """
        return f'yfinance.Sector object <{self._key}>'
    
    @property
    def top_etfs(self) -> Dict[str, str]:
        """
        获取板块的顶尖ETF。

        返回:
            Dict[str, str]: ETF符号和名称的字典。
        """
        self._ensure_fetched(self._top_etfs)
        return self._top_etfs

    @property
    def top_mutual_funds(self) -> Dict[str, str]:
        """
        获取板块的顶尖共同基金。

        返回:
            Dict[str, str]: 共同基金符号和名称的字典。
        """
        self._ensure_fetched(self._top_mutual_funds)
        return self._top_mutual_funds

    @dynamic_docstring({"sector_industry": generate_list_table_from_dict(SECTOR_INDUSTY_MAPPING,bullets=True)})
    @property
    def industries(self) -> _pd.DataFrame:
        """
        获取板块内的行业。

        返回:
            pandas.DataFrame: 包含行业键、名称、符号和市场权重的DataFrame。

        {sector_industry}
        """
        self._ensure_fetched(self._industries)
        return self._industries
    
    def _parse_top_etfs(self, top_etfs: Dict) -> Dict[str, str]:
        """
        从API响应中解析顶尖ETF数据。

        参数:
            top_etfs (Dict): 来自API响应的原始ETF数据。

        返回:
            Dict[str, str]: ETF符号和名称的字典。
        """
        return {e.get('symbol'): e.get('name') for e in top_etfs}

    def _parse_top_mutual_funds(self, top_mutual_funds: Dict) -> Dict[str, str]:
        """
        从API响应中解析顶尖共同基金数据。

        参数:
            top_mutual_funds (Dict): 来自API响应的原始共同基金数据。

        返回:
            Dict[str, str]: 共同基金符号和名称的字典。
        """
        return {e.get('symbol'): e.get('name') for e in top_mutual_funds}
    
    def _parse_industries(self, industries: Dict) -> _pd.DataFrame:
        """
        从API响应中将行业数据解析为DataFrame。

        参数:
            industries (Dict): 来自API响应的原始行业数据。

        返回:
            pandas.DataFrame: 包含行业键、名称、符号和市场权重的DataFrame。
        """
        industries_column = ['key','name','symbol','market weight']
        industries_values = [(i.get('key'),
                              i.get('name'),
                              i.get('symbol'),
                              i.get('marketWeight',{}).get('raw', None)
                              ) for i in industries if i.get('name') != 'All Industries']
        return _pd.DataFrame(industries_values, columns=industries_column).set_index('key')

    def _fetch_and_parse(self) -> None:
        """
        从API获取并解析板块数据。

        获取板块数据，并解析板块内的顶尖ETF、顶尖共同基金和行业。
        将解析后的数据存储在相应的属性 `_top_etfs`、`_top_mutual_funds` 和 `_industries` 中。

        引发:
            Exception: 如果获取或解析板块数据失败。
        """
        result = None
        
        try:
            result = self._fetch(self._query_url)
            data = result['data']
            self._parse_and_assign_common(data)

            self._top_etfs = self._parse_top_etfs(data.get('topETFs', {}))
            self._top_mutual_funds = self._parse_top_mutual_funds(data.get('topMutualFunds', {}))
            self._industries = self._parse_industries(data.get('industries', {}))

        except Exception as e:
            logger = get_yf_logger()
            logger.error(f"Failed to get sector data for '{self._key}' reason: {e}")
            logger.debug("Got response: ")
            logger.debug("-------------")
            logger.debug(f" {result}")
            logger.debug("-------------")
