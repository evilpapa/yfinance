import pandas as pd
from typing import Dict, Any, Optional

from .base import DataSourceStrategy
from ..data import YfData
from ..const import _BASE_URL_, _QUERY1_URL_

_QUOTE_SUMMARY_URL_ = f"{_BASE_URL_}/v10/finance/quoteSummary"

class YahooDataSource(DataSourceStrategy):
    """
    雅虎财经的数据源实现。
    Data source implementation for Yahoo Finance.

    这个类包含了从雅虎财经API获取和解析数据的具体逻辑。
    它被设计为默认的数据源。
    """

    def __init__(self):
        # YfData 是一个单例, 所以每次实例化都会获得同一个对象
        # YfData is a singleton, so this will always get the same object
        self._data_fetcher = YfData()

    def get_info(self, ticker: str, proxy: Optional[str] = None, timeout: Optional[int] = None) -> Dict[str, Any]:
        """
        获取、解析并格式化指定股票的 'info' 数据。
        这里的逻辑是从旧的 scraper 中迁移过来的，以确保100%的兼容性。
        """

        # 1. 从多个API端点获取原始JSON数据
        modules = ['financialData', 'quoteType', 'defaultKeyStatistics', 'assetProfile', 'summaryDetail']
        params = {"modules": ",".join(modules)}

        try:
            summary_result = self._data_fetcher.get_raw_json(f"{_QUOTE_SUMMARY_URL_}/{ticker}", params=params)
        except Exception:
            summary_result = None

        try:
            quote_result = self._data_fetcher.get_raw_json(f"{_QUERY1_URL_}/v7/finance/quote?", params={"symbols": ticker})
        except Exception:
            quote_result = None

        # 2. 合并和处理JSON数据
        info = {}
        if summary_result:
            info.update(summary_result)
        if quote_result:
            info.update(quote_result)

        if not info:
            return {}

        processed_info = {}
        for quote_key in ["quoteSummary", "quoteResponse"]:
            if quote_key in info and info[quote_key]["result"]:
                for res in info[quote_key]["result"]:
                    if res.get("symbol") == ticker:
                        processed_info.update(res)
                        break

        # 3. 扁平化处理，因为API返回的数据是嵌套的
        flattened_info = {}
        for k, v in processed_info.items():
            if isinstance(v, dict):
                flattened_info.update(v)
            else:
                flattened_info[k] = v

        # 4. 最终格式化，提取 'raw' 值
        final_info = {}
        for k, v in flattened_info.items():
            if isinstance(v, dict) and "raw" in v:
                final_info[k] = v["raw"]
            elif v is not None and not (isinstance(v, (dict, list)) and not v):
                final_info[k] = v

        if 'symbol' not in final_info:
            final_info['symbol'] = ticker

        return final_info

    # 其他方法暂未实现
    def get_history(self, ticker: str, period: str, interval: str,
                    start: Optional[str] = None, end: Optional[str] = None,
                    **kwargs) -> Optional[pd.DataFrame]:
        raise NotImplementedError("History has not been migrated to YahooDataSource yet.")

    def get_income_stmt(self, ticker: str, **kwargs) -> Optional[pd.DataFrame]:
        raise NotImplementedError("Financials have not been migrated to YahooDataSource yet.")

    def get_balance_sheet(self, ticker: str, **kwargs) -> Optional[pd.DataFrame]:
        raise NotImplementedError("Financials have not been migrated to YahooDataSource yet.")

    def get_cash_flow(self, ticker: str, **kwargs) -> Optional[pd.DataFrame]:
        raise NotImplementedError("Financials have not been migrated to YahooDataSource yet.")
