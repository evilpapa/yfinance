#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
数据源策略抽象基类

该模块定义了数据源的抽象接口，所有具体的数据源实现都必须继承并实现这个抽象基类。
这遵循了策略模式的设计原则，使得不同数据源可以无缝切换。
"""

from abc import ABC, abstractmethod
from typing import Optional, Union, Dict, List
import pandas as pd


class DataSourceStrategy(ABC):
    """
    数据源策略抽象基类
    
    定义了所有数据源必须实现的接口方法。这个抽象基类确保了：
    1. 不同数据源具有统一的接口
    2. 可以轻松添加新的数据源
    3. 数据源之间可以无缝切换
    4. 支持多种市场和证券类型
    """

    def __init__(self, ticker: str):
        """
        初始化数据源策略
        
        Args:
            ticker: 股票代码或证券标识符
        """
        self.ticker = ticker.upper()
        self._validate_ticker()

    @abstractmethod
    def _validate_ticker(self) -> bool:
        """
        验证股票代码是否适用于当前数据源
        
        Returns:
            bool: 如果股票代码有效则返回 True
        
        Raises:
            ValueError: 如果股票代码无效
        """
        pass

    @abstractmethod
    def supports_ticker(self, ticker: str) -> bool:
        """
        检查数据源是否支持指定的股票代码
        
        Args:
            ticker: 股票代码
            
        Returns:
            bool: 如果支持该股票代码则返回 True
        """
        pass

    # =========================
    # 基础信息接口
    # =========================

    @abstractmethod
    def get_info(self) -> Dict:
        """
        获取股票基本信息
        
        Returns:
            Dict: 包含股票基本信息的字典，标准键包括：
                - symbol: 股票代码
                - longName: 公司全名
                - shortName: 公司简称
                - marketCap: 市值
                - currency: 货币单位
                - exchange: 交易所
                - industry: 行业
                - sector: 板块
                - country: 国家
                - website: 官网
                - fullTimeEmployees: 员工数量
        """
        pass

    @abstractmethod
    def get_fast_info(self) -> Dict:
        """
        获取快速基本信息（性能优化版本）
        
        Returns:
            Dict: 包含关键信息的字典，如最新价、市值等
        """
        pass

    # =========================
    # 历史数据接口
    # =========================

    @abstractmethod
    def get_history(self, period: str = "1y", interval: str = "1d", 
                   start: Optional[str] = None, end: Optional[str] = None) -> pd.DataFrame:
        """
        获取历史价格数据
        
        Args:
            period: 时间段，如 "1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"
            interval: 数据间隔，如 "1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h", "1d", "5d", "1wk", "1mo", "3mo"
            start: 开始日期 (YYYY-MM-DD)
            end: 结束日期 (YYYY-MM-DD)
            
        Returns:
            pd.DataFrame: 历史价格数据，包含列：
                - Open: 开盘价
                - High: 最高价
                - Low: 最低价
                - Close: 收盘价
                - Volume: 成交量
                - Adj Close: 复权收盘价（如果适用）
        """
        pass

    @abstractmethod
    def get_dividends(self, period: str = "max") -> pd.Series:
        """
        获取股息数据
        
        Args:
            period: 时间段
            
        Returns:
            pd.Series: 股息数据时间序列
        """
        pass

    @abstractmethod
    def get_splits(self, period: str = "max") -> pd.Series:
        """
        获取股票分割数据
        
        Args:
            period: 时间段
            
        Returns:
            pd.Series: 股票分割数据时间序列
        """
        pass

    @abstractmethod
    def get_actions(self, period: str = "max") -> pd.DataFrame:
        """
        获取公司行动数据（股息+分割）
        
        Args:
            period: 时间段
            
        Returns:
            pd.DataFrame: 公司行动数据
        """
        pass

    # =========================
    # 财务数据接口
    # =========================

    @abstractmethod
    def get_financials(self, freq: str = "yearly") -> pd.DataFrame:
        """
        获取财务数据（利润表）
        
        Args:
            freq: 频率，"yearly"（年度）或 "quarterly"（季度）
            
        Returns:
            pd.DataFrame: 财务数据
        """
        pass

    @abstractmethod
    def get_balance_sheet(self, freq: str = "yearly") -> pd.DataFrame:
        """
        获取资产负债表
        
        Args:
            freq: 频率，"yearly"（年度）或 "quarterly"（季度）
            
        Returns:
            pd.DataFrame: 资产负债表数据
        """
        pass

    @abstractmethod
    def get_cash_flow(self, freq: str = "yearly") -> pd.DataFrame:
        """
        获取现金流量表
        
        Args:
            freq: 频率，"yearly"（年度）或 "quarterly"（季度）
            
        Returns:
            pd.DataFrame: 现金流量表数据
        """
        pass

    @abstractmethod
    def get_earnings(self, freq: str = "yearly") -> Optional[pd.DataFrame]:
        """
        获取收益数据
        
        Args:
            freq: 频率，"yearly"（年度）或 "quarterly"（季度）
            
        Returns:
            Optional[pd.DataFrame]: 收益数据，如果不可用则返回 None
        """
        pass

    # =========================
    # 持股信息接口
    # =========================

    @abstractmethod
    def get_major_holders(self) -> pd.DataFrame:
        """
        获取主要持股者信息
        
        Returns:
            pd.DataFrame: 主要持股者数据
        """
        pass

    @abstractmethod
    def get_institutional_holders(self) -> Optional[pd.DataFrame]:
        """
        获取机构持股者信息
        
        Returns:
            Optional[pd.DataFrame]: 机构持股者数据，如果不可用则返回 None
        """
        pass

    @abstractmethod
    def get_insider_transactions(self) -> Optional[pd.DataFrame]:
        """
        获取内部人员交易信息
        
        Returns:
            Optional[pd.DataFrame]: 内部人员交易数据，如果不可用则返回 None
        """
        pass

    # =========================
    # 分析数据接口
    # =========================

    @abstractmethod
    def get_recommendations(self) -> Optional[pd.DataFrame]:
        """
        获取分析师推荐信息
        
        Returns:
            Optional[pd.DataFrame]: 分析师推荐数据，如果不可用则返回 None
        """
        pass

    @abstractmethod
    def get_analyst_price_targets(self) -> Optional[Dict]:
        """
        获取分析师目标价信息
        
        Returns:
            Optional[Dict]: 目标价数据，如果不可用则返回 None
        """
        pass

    @abstractmethod
    def get_earnings_estimate(self) -> Optional[pd.DataFrame]:
        """
        获取收益预估信息
        
        Returns:
            Optional[pd.DataFrame]: 收益预估数据，如果不可用则返回 None
        """
        pass

    # =========================
    # 新闻和日历接口
    # =========================

    @abstractmethod
    def get_news(self, count: int = 10) -> List[Dict]:
        """
        获取相关新闻
        
        Args:
            count: 新闻数量
            
        Returns:
            List[Dict]: 新闻列表
        """
        pass

    @abstractmethod
    def get_calendar(self) -> Optional[Dict]:
        """
        获取财报日历
        
        Returns:
            Optional[Dict]: 财报日历数据，如果不可用则返回 None
        """
        pass

    @abstractmethod
    def get_earnings_dates(self, limit: int = 12) -> Optional[pd.DataFrame]:
        """
        获取财报日期
        
        Args:
            limit: 限制返回的数量
            
        Returns:
            Optional[pd.DataFrame]: 财报日期数据，如果不可用则返回 None
        """
        pass

    # =========================
    # 其他数据接口
    # =========================

    @abstractmethod
    def get_sustainability(self) -> Optional[pd.DataFrame]:
        """
        获取可持续性数据
        
        Returns:
            Optional[pd.DataFrame]: 可持续性数据，如果不可用则返回 None
        """
        pass

    @abstractmethod
    def get_shares(self) -> Optional[pd.DataFrame]:
        """
        获取股份信息
        
        Returns:
            Optional[pd.DataFrame]: 股份信息，如果不可用则返回 None
        """
        pass

    @abstractmethod
    def get_isin(self) -> Optional[str]:
        """
        获取 ISIN 代码
        
        Returns:
            Optional[str]: ISIN 代码，如果不可用则返回 None
        """
        pass

    # =========================
    # 元数据接口
    # =========================

    @abstractmethod
    def get_history_metadata(self) -> Dict:
        """
        获取历史数据元信息
        
        Returns:
            Dict: 元数据信息
        """
        pass

    @abstractmethod
    def get_source_name(self) -> str:
        """
        获取数据源名称
        
        Returns:
            str: 数据源名称
        """
        pass

    @abstractmethod
    def get_supported_markets(self) -> List[str]:
        """
        获取支持的市场列表
        
        Returns:
            List[str]: 支持的市场代码列表
        """
        pass

    # =========================
    # 工具方法
    # =========================

    def is_market_open(self) -> bool:
        """
        检查市场是否开放
        
        Returns:
            bool: 如果市场开放则返回 True
        """
        # 默认实现，子类可以重写
        return True

    def get_timezone(self) -> str:
        """
        获取市场时区
        
        Returns:
            str: 时区字符串
        """
        # 默认实现，子类可以重写
        return "UTC"

    def __repr__(self) -> str:
        """字符串表示"""
        return f"{self.__class__.__name__}(ticker='{self.ticker}')"
