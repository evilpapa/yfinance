from __future__ import print_function

import pandas as _pd
from typing import Dict, Optional
import warnings

from .. import utils
from ..const import _SENTINEL_
from ..data import YfData

from .domain import Domain, _QUERY_URL_

class Industry(Domain):
    """
    表示行业内的特定行业。
    """

    def __init__(self, key, session=None, proxy=_SENTINEL_):
        """
        参数:
            key (str): 行业的键标识符。
            session (optional): 用于请求的会话。
        """
        if proxy is not _SENTINEL_:
            warnings.warn("Set proxy via new config function: yf.set_config(proxy=proxy)", DeprecationWarning, stacklevel=2)
            YfData(proxy=proxy)
        YfData(session=session)
        super(Industry, self).__init__(key, session)
        self._query_url = f'{_QUERY_URL_}/industries/{self._key}'

        self._sector_key = None
        self._sector_name = None
        self._top_performing_companies = None
        self._top_growth_companies = None

    def __repr__(self):
        """
        返回Industry实例的字符串表示形式。
        
        返回:
            str: Industry实例的字符串表示形式。
        """
        return f'yfinance.Industry object <{self._key}>'
    
    @property
    def sector_key(self) -> str:
        """
        返回行业的板块键。
        
        返回:
            str: 板块键。
        """
        self._ensure_fetched(self._sector_key)
        return self._sector_key
    
    @property
    def sector_name(self) -> str:
        """
        返回行业的板块名称。
        
        返回:
            str: 板块名称。
        """
        self._ensure_fetched(self._sector_name)
        return self._sector_name
    
    @property
    def top_performing_companies(self) -> Optional[_pd.DataFrame]:
        """
        返回行业中表现最佳的公司。
        
        返回:
            Optional[pd.DataFrame]: 包含表现最佳公司的DataFrame。
        """
        self._ensure_fetched(self._top_performing_companies)
        return self._top_performing_companies
    
    @property
    def top_growth_companies(self) -> Optional[_pd.DataFrame]:
        """
        返回行业中增长最快的公司。
        
        返回:
            Optional[pd.DataFrame]: 包含增长最快公司的DataFrame。
        """
        self._ensure_fetched(self._top_growth_companies)
        return self._top_growth_companies
    
    def _parse_top_performing_companies(self, top_performing_companies: Dict) -> Optional[_pd.DataFrame]:
        """
        解析表现最佳的公司数据。
        
        参数:
            top_performing_companies (Dict): 包含表现最佳公司数据的字典。
        
        返回:
            Optional[pd.DataFrame]: 包含已解析的表现最佳公司数据的DataFrame。
        """
        compnaies_column = ['symbol','name','ytd return',' last price','target price']
        compnaies_values = [(c.get('symbol', None),
                             c.get('name', None),
                             c.get('ytdReturn',{}).get('raw', None),
                             c.get('lastPrice',{}).get('raw', None),
                             c.get('targetPrice',{}).get('raw', None),) for c in top_performing_companies]
        
        if not compnaies_values: 
            return None

        return _pd.DataFrame(compnaies_values, columns = compnaies_column).set_index('symbol')
    
    def _parse_top_growth_companies(self, top_growth_companies: Dict) -> Optional[_pd.DataFrame]:
        """
        解析增长最快的公司数据。
        
        参数:
            top_growth_companies (Dict): 包含增长最快公司数据的字典。
        
        返回:
            Optional[pd.DataFrame]: 包含已解析的增长最快公司数据的DataFrame。
        """
        compnaies_column = ['symbol','name','ytd return',' growth estimate']
        compnaies_values = [(c.get('symbol', None),
                             c.get('name', None),
                             c.get('ytdReturn',{}).get('raw', None),
                             c.get('growthEstimate',{}).get('raw', None),) for c in top_growth_companies]
        
        if not compnaies_values: 
            return None

        return _pd.DataFrame(compnaies_values, columns = compnaies_column).set_index('symbol')

    def _fetch_and_parse(self) -> None:
        """
        获取并解析行业数据。
        """
        result = None
        
        try:
            result = self._fetch(self._query_url)
            data = result['data']
            self._parse_and_assign_common(data)

            self._sector_key = data.get('sectorKey')
            self._sector_name = data.get('sectorName')
            self._top_performing_companies = self._parse_top_performing_companies(data.get('topPerformingCompanies'))
            self._top_growth_companies = self._parse_top_growth_companies(data.get('topGrowthCompanies'))

            return result
        except Exception as e:
            logger = utils.get_yf_logger()
            logger.error(f"Failed to get industry data for '{self._key}' reason: {e}")
            logger.debug("Got response: ")
            logger.debug("-------------")
            logger.debug(f" {result}")
            logger.debug("-------------")
