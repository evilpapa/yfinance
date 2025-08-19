import abc
import pandas as pd
from typing import Dict, Any, Optional

class DataSourceStrategy(abc.ABC):
    """
    数据源策略的抽象基类 (Abstract Base Class for data source strategies)。

    该类定义了一个通用接口，所有具体的数据源实现（如 Yahoo, Akshare）都必须遵循这个接口。
    这确保了上层逻辑可以统一地调用不同的数据源。
    """

    @abc.abstractmethod
    def get_history(self, ticker: str, period: str, interval: str,
                    start: Optional[str] = None, end: Optional[str] = None,
                    **kwargs) -> Optional[pd.DataFrame]:
        """
        获取指定股票的历史行情数据。
        Fetches historical market data for a given ticker.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_info(self, ticker: str, proxy: Optional[str] = None, timeout: Optional[int] = None) -> Dict[str, Any]:
        """
        获取指定股票的基本信息。
        Fetches general information about the ticker.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_income_stmt(self, ticker: str, proxy: Optional[str] = None, timeout: Optional[int] = None,
                          freq: str = "yearly") -> Optional[pd.DataFrame]:
        """
        获取利润表。
        Fetches income statement.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_balance_sheet(self, ticker: str, proxy: Optional[str] = None, timeout: Optional[int] = None,
                            freq: str = "yearly") -> Optional[pd.DataFrame]:
        """
        获取资产负债表。
        Fetches balance sheet.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_cash_flow(self, ticker: str, proxy: Optional[str] = None, timeout: Optional[int] = None,
                        freq: str = "yearly") -> Optional[pd.DataFrame]:
        """
        获取现金流量表。
        Fetches cash flow statement.
        """
        raise NotImplementedError
