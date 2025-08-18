import abc
import pandas as pd
from typing import Dict, Any, Optional

class DataSourceStrategy(abc.ABC):
    """
    Abstract Base Class for data source strategies.
    Defines a common interface for fetching financial data from various sources.
    """

    @abc.abstractmethod
    def get_history(self, ticker: str, period: str, interval: str,
                    start: Optional[str] = None, end: Optional[str] = None,
                    prepost: bool = False, actions: bool = True,
                    auto_adjust: bool = True, back_adjust: bool = False,
                    proxy: Optional[str] = None, rounding: bool = False,
                    tz: Optional[str] = None, timeout: Optional[int] = None,
                    **kwargs) -> Optional[pd.DataFrame]:
        """Fetches historical market data."""
        raise NotImplementedError

    @abc.abstractmethod
    def get_info(self, ticker: str, proxy: Optional[str] = None, timeout: Optional[int] = None) -> Dict[str, Any]:
        """Fetches general information about the ticker."""
        raise NotImplementedError

    @abc.abstractmethod
    def get_major_holders(self, ticker: str, proxy: Optional[str] = None, timeout: Optional[int] = None) -> Optional[pd.DataFrame]:
        """Fetches major holders data."""
        raise NotImplementedError

    @abc.abstractmethod
    def get_institutional_holders(self, ticker: str, proxy: Optional[str] = None, timeout: Optional[int] = None) -> Optional[pd.DataFrame]:
        """Fetches institutional holders data."""
        raise NotImplementedError

    @abc.abstractmethod
    def get_income_stmt(self, ticker: str, proxy: Optional[str] = None, timeout: Optional[int] = None,
                          freq: str = "yearly") -> Optional[pd.DataFrame]:
        """Fetches income statement."""
        raise NotImplementedError

    @abc.abstractmethod
    def get_balance_sheet(self, ticker: str, proxy: Optional[str] = None, timeout: Optional[int] = None,
                            freq: str = "yearly") -> Optional[pd.DataFrame]:
        """Fetches balance sheet."""
        raise NotImplementedError

    @abc.abstractmethod
    def get_cash_flow(self, ticker: str, proxy: Optional[str] = None, timeout: Optional[int] = None,
                        freq: str = "yearly") -> Optional[pd.DataFrame]:
        """Fetches cash flow statement."""
        raise NotImplementedError

    @abc.abstractmethod
    def get_recommendations(self, ticker: str, proxy: Optional[str] = None, timeout: Optional[int] = None) -> Optional[pd.DataFrame]:
        """Fetches analyst recommendations."""
        raise NotImplementedError

    @abc.abstractmethod
    def get_earnings_dates(self, ticker: str, proxy: Optional[str] = None, timeout: Optional[int] = None) -> Optional[pd.DataFrame]:
        """Fetches earnings dates."""
        raise NotImplementedError
