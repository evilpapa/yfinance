import pandas as pd
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Union

from yfinance.scrapers.funds import FundsData


class DataSourceStrategy(ABC):
    """
    Ticker 抽象基类

    定义了所有 Ticker 类属性方法所依赖的抽象接口。
    任何想要被 Ticker 类使用的实现都必须继承此抽象基类并实现所有抽象方法。
    """

    @abstractmethod
    def get_history(self, ticker: str, period: str, interval: str,
                    start: Optional[str] = None, end: Optional[str] = None,
                    **kwargs) -> Optional[pd.DataFrame]:
        """
        获取指定股票的历史行情数据。
        Fetches historical market data for a given ticker.
        """
        pass

    @abstractmethod
    def get_isin(self, proxy=None) -> Optional[str]:
        """
        获取股票的 ISIN (国际证券识别号码)

        Args:
            proxy: 代理设置（已弃用）

        Returns:
            Optional[str]: ISIN 号码，如果无法获取则返回 None
        """
        pass

    @abstractmethod
    def get_major_holders(self, proxy=None, as_dict=False) -> pd.DataFrame:
        """
        获取主要持股者信息

        Args:
            proxy: 代理设置（已弃用）
            as_dict: 是否返回字典格式

        Returns:
            pd.DataFrame: 主要持股者数据
        """
        pass

    @abstractmethod
    def get_institutional_holders(self, proxy=None, as_dict=False) -> Optional[pd.DataFrame]:
        """
        获取机构持股者信息

        Args:
            proxy: 代理设置（已弃用）
            as_dict: 是否返回字典格式

        Returns:
            Optional[pd.DataFrame]: 机构持股者数据，如果无数据则返回 None
        """
        pass

    @abstractmethod
    def get_mutualfund_holders(self, proxy=None, as_dict=False) -> Optional[pd.DataFrame]:
        """
        获取共同基金持股者信息

        Args:
            proxy: 代理设置（已弃用）
            as_dict: 是否返回字典格式

        Returns:
            Optional[pd.DataFrame]: 共同基金持股者数据，如果无数据则返回 None
        """
        pass

    @abstractmethod
    def get_insider_purchases(self, proxy=None, as_dict=False) -> Optional[pd.DataFrame]:
        """
        获取内部人员购买信息

        Args:
            proxy: 代理设置（已弃用）
            as_dict: 是否返回字典格式

        Returns:
            Optional[pd.DataFrame]: 内部人员购买数据，如果无数据则返回 None
        """
        pass

    @abstractmethod
    def get_insider_transactions(self, proxy=None, as_dict=False) -> Optional[pd.DataFrame]:
        """
        获取内部人员交易信息

        Args:
            proxy: 代理设置（已弃用）
            as_dict: 是否返回字典格式

        Returns:
            Optional[pd.DataFrame]: 内部人员交易数据，如果无数据则返回 None
        """
        pass

    @abstractmethod
    def get_insider_roster_holders(self, proxy=None, as_dict=False) -> Optional[pd.DataFrame]:
        """
        获取内部人员名单持股者信息

        Args:
            proxy: 代理设置（已弃用）
            as_dict: 是否返回字典格式

        Returns:
            Optional[pd.DataFrame]: 内部人员名单持股者数据，如果无数据则返回 None
        """
        pass

    @abstractmethod
    def get_dividends(self, proxy=None, period="max") -> pd.Series:
        """
        获取股息信息

        Args:
            proxy: 代理设置（已弃用）
            period: 时间周期，默认为 "max"

        Returns:
            pd.Series: 股息数据时间序列
        """
        pass

    @abstractmethod
    def get_capital_gains(self, proxy=None, period="max") -> pd.Series:
        """
        获取资本增值信息

        Args:
            proxy: 代理设置（已弃用）
            period: 时间周期，默认为 "max"

        Returns:
            pd.Series: 资本增值数据时间序列
        """
        pass

    @abstractmethod
    def get_splits(self, proxy=None, period="max") -> pd.Series:
        """
        获取股票分割信息

        Args:
            proxy: 代理设置（已弃用）
            period: 时间周期，默认为 "max"

        Returns:
            pd.Series: 股票分割数据时间序列
        """
        pass

    @abstractmethod
    def get_actions(self, proxy=None, period="max") -> pd.Series:
        """
        获取股票操作信息（包括股息、分割等）

        Args:
            proxy: 代理设置（已弃用）
            period: 时间周期，默认为 "max"

        Returns:
            pd.Series: 股票操作数据时间序列
        """
        pass

    @abstractmethod
    def get_shares(self, proxy=None, as_dict=False) -> Union[pd.DataFrame, dict]:
        """
        获取股份信息

        Args:
            proxy: 代理设置（已弃用）
            as_dict: 是否返回字典格式

        Returns:
            Union[pd.DataFrame, dict]: 股份数据
        """
        pass

    @abstractmethod
    def get_shares_full(self, proxy=None, as_dict=False) -> pd.Series:
        """
        获取股份信息

        Args:
            proxy: 代理设置（已弃用）
            as_dict: 是否返回字典格式

        Returns:
            pd.Series: 股份数据
        """
        pass

    @abstractmethod
    def get_info(self, proxy=None) -> dict:
        """
        获取股票基本信息

        Args:
            proxy: 代理设置（已弃用）

        Returns:
            dict: 股票基本信息字典
        """
        pass

    @abstractmethod
    def get_fast_info(self, proxy=None):
        """
        获取快速访问的股票信息

        Args:
            proxy: 代理设置（已弃用）

        Returns:
            FastInfo: 快速信息对象
        """
        pass

    @abstractmethod
    def get_calendar(self, proxy=None) -> dict:
        """
        获取财报日历信息

        Args:
            proxy: 代理设置（已弃用）

        Returns:
            dict: 财报日历信息字典
        """
        pass

    @abstractmethod
    def get_sec_filings(self, proxy=None) -> dict:
        """
        获取 SEC 文件提交信息

        Args:
            proxy: 代理设置（已弃用）

        Returns:
            dict: SEC 文件提交信息字典
        """
        pass

    @abstractmethod
    def get_recommendations(self, proxy=None, as_dict=False) -> pd.DataFrame:
        """
        获取分析师推荐信息

        Args:
            proxy: 代理设置（已弃用）
            as_dict: 是否返回字典格式

        Returns:
            pd.DataFrame: 分析师推荐数据
        """
        pass

    @abstractmethod
    def get_recommendations_summary(self, proxy=None, as_dict=False) -> pd.DataFrame:
        """
        获取分析师推荐汇总信息

        Args:
            proxy: 代理设置（已弃用）
            as_dict: 是否返回字典格式

        Returns:
            pd.DataFrame: 分析师推荐汇总数据
        """
        pass

    @abstractmethod
    def get_upgrades_downgrades(self, proxy=None, as_dict=False) -> pd.DataFrame:
        """
        获取评级上调/下调信息

        Args:
            proxy: 代理设置（已弃用）
            as_dict: 是否返回字典格式

        Returns:
            pd.DataFrame: 评级上调/下调数据
        """
        pass

    @abstractmethod
    def get_earnings(self, proxy=None, as_dict=False, freq="yearly") -> Optional[pd.DataFrame]:
        """
        获取收益信息

        Args:
            proxy: 代理设置（已弃用）
            as_dict: 是否返回字典格式
            freq: 频率，可选 "yearly", "quarterly", "trailing"

        Returns:
            Optional[pd.DataFrame]: 收益数据，如果无数据则返回 None
        """
        pass

    @abstractmethod
    def get_income_stmt(self, proxy=None, as_dict=False, pretty=False, freq="yearly") -> pd.DataFrame:
        """
        获取利润表信息

        Args:
            proxy: 代理设置（已弃用）
            as_dict: 是否返回字典格式
            pretty: 是否美化行名称
            freq: 频率，可选 "yearly", "quarterly", "trailing"

        Returns:
            pd.DataFrame: 利润表数据
        """
        pass

    @abstractmethod
    def get_balance_sheet(self, proxy=None, as_dict=False, pretty=False, freq="yearly") -> pd.DataFrame:
        """
        获取资产负债表信息

        Args:
            proxy: 代理设置（已弃用）
            as_dict: 是否返回字典格式
            pretty: 是否美化行名称
            freq: 频率，可选 "yearly", "quarterly"

        Returns:
            pd.DataFrame: 资产负债表数据
        """
        pass

    @abstractmethod
    def get_cash_flow(self, proxy=None, as_dict=False, pretty=False, freq="yearly") -> Union[pd.DataFrame, dict]:
        """
        获取现金流量表信息

        Args:
            proxy: 代理设置（已弃用）
            as_dict: 是否返回字典格式
            pretty: 是否美化行名称
            freq: 频率，可选 "yearly", "quarterly", "trailing"

        Returns:
            Union[pd.DataFrame, dict]: 现金流量表数据
        """
        pass

    @abstractmethod
    def get_analyst_price_targets(self, proxy=None) -> dict:
        """
        获取分析师目标价信息

        Args:
            proxy: 代理设置（已弃用）

        Returns:
            dict: 分析师目标价数据字典，包含 current, low, high, mean, median 等键
        """
        pass

    @abstractmethod
    def get_earnings_estimate(self, proxy=None, as_dict=False) -> pd.DataFrame:
        """
        获取收益预估信息

        Args:
            proxy: 代理设置（已弃用）
            as_dict: 是否返回字典格式

        Returns:
            pd.DataFrame: 收益预估数据
        """
        pass

    @abstractmethod
    def get_revenue_estimate(self, proxy=None, as_dict=False) -> pd.DataFrame:
        """
        获取营收预估信息

        Args:
            proxy: 代理设置（已弃用）
            as_dict: 是否返回字典格式

        Returns:
            pd.DataFrame: 营收预估数据
        """
        pass

    @abstractmethod
    def get_earnings_history(self, proxy=None, as_dict=False) -> pd.DataFrame:
        """
        获取收益历史信息

        Args:
            proxy: 代理设置（已弃用）
            as_dict: 是否返回字典格式

        Returns:
            pd.DataFrame: 收益历史数据
        """
        pass

    @abstractmethod
    def get_eps_trend(self, proxy=None, as_dict=False) -> pd.DataFrame:
        """
        获取每股收益趋势信息

        Args:
            proxy: 代理设置（已弃用）
            as_dict: 是否返回字典格式

        Returns:
            pd.DataFrame: 每股收益趋势数据
        """
        pass

    @abstractmethod
    def get_eps_revisions(self, proxy=None, as_dict=False) -> pd.DataFrame:
        """
        获取每股收益修正信息

        Args:
            proxy: 代理设置（已弃用）
            as_dict: 是否返回字典格式

        Returns:
            pd.DataFrame: 每股收益修正数据
        """
        pass

    @abstractmethod
    def get_growth_estimates(self, proxy=None, as_dict=False) -> pd.DataFrame:
        """
        获取增长预估信息

        Args:
            proxy: 代理设置（已弃用）
            as_dict: 是否返回字典格式

        Returns:
            pd.DataFrame: 增长预估数据
        """
        pass

    @abstractmethod
    def get_sustainability(self, proxy=None, as_dict=False) -> pd.DataFrame:
        """
        获取可持续性信息

        Args:
            proxy: 代理设置（已弃用）
            as_dict: 是否返回字典格式

        Returns:
            pd.DataFrame: 可持续性数据
        """
        pass

    @abstractmethod
    def get_news(self, count=10, tab="news", proxy=None) -> list:
        """
        获取新闻信息

        Args:
            count: 新闻数量，默认为 10
            tab: 新闻标签，可选 "news", "all", "press releases"
            proxy: 代理设置（已弃用）

        Returns:
            list: 新闻列表
        """
        pass

    @abstractmethod
    def get_earnings_dates(self, limit=12, proxy=None) -> Optional[pd.DataFrame]:
        """
        获取财报日期信息

        Args:
            limit: 限制数量，默认为 12
            proxy: 代理设置（已弃用）

        Returns:
            Optional[pd.DataFrame]: 财报日期数据，如果无数据则返回 None
        """
        pass

    @abstractmethod
    def get_history_metadata(self, proxy=None) -> dict:
        """
        获取历史数据元信息

        Args:
            proxy: 代理设置（已弃用）

        Returns:
            dict: 历史数据元信息字典
        """
        pass

    @abstractmethod
    def get_funds_data(self, proxy=None) -> Optional[FundsData]:
        """
        获取基金数据信息

        Args:
            proxy: 代理设置（已弃用）

        Returns:
            Optional[FundsData]: 基金数据对象，如果无数据则返回 None
        """
        pass

    def live(self, self1, message_handler, verbose):
        pass
