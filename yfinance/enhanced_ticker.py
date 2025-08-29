#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
增强版 Ticker 类

集成了新的多数据源架构，支持从多个数据提供商获取金融数据。
"""

from __future__ import print_function

from collections import namedtuple as _namedtuple
import warnings
from typing import Optional, Union, Dict, List

import pandas as pd

# 导入新的数据源架构
from .datasources import get_data_source, DataSourceStrategy
from .datasources.yahoo_datasource import YahooDataSource

# 保持与原版本的兼容性
from .base import TickerBase
from .const import _BASE_URL_, _SENTINEL_


class MultiSourceTicker:
    """
    多数据源股票数据获取器
    
    该类自动选择最适合的数据源来获取股票数据，支持：
    - Yahoo Finance（全球市场）
    - AKShare（中国A股市场）
    
    自动根据股票代码格式选择最合适的数据源。
    """
    
    def __init__(self, ticker: str, preferred_source: str = None, session=None, proxy=_SENTINEL_):
        """
        初始化多数据源股票对象
        
        Args:
            ticker: 股票代码
            preferred_source: 首选数据源（可选，如 'yahoo', 'akshare'）
            session: HTTP会话对象（仅用于Yahoo Finance）
            proxy: 代理设置（已弃用，使用配置函数）
        """
        if proxy is not _SENTINEL_:
            warnings.warn(
                "Set proxy via new config function: yf.set_config(proxy=proxy)", 
                DeprecationWarning, 
                stacklevel=2
            )
        
        self.ticker = ticker.upper().strip()
        self._preferred_source = preferred_source
        self._session = session
        
        # 获取最适合的数据源
        try:
            if preferred_source == 'yahoo' and session:
                # 如果明确指定 Yahoo Finance 且提供了 session，直接创建
                self._data_source = YahooDataSource(self.ticker, session=session)
            else:
                # 使用工厂方法自动选择数据源
                self._data_source = get_data_source(self.ticker, preferred_source)
                
                # 如果是 Yahoo 数据源且提供了 session，更新 session
                if isinstance(self._data_source, YahooDataSource) and session:
                    self._data_source.session = session
                    self._data_source._data.session = session
                    
        except ValueError as e:
            # 如果没找到合适的数据源，默认使用 Yahoo Finance
            warnings.warn(f"自动数据源选择失败: {e}，回退到 Yahoo Finance")
            self._data_source = YahooDataSource(self.ticker, session=session)
        
        # 为了向后兼容，保留一些属性
        self._expirations = {}
        self._underlying = {}

    def __repr__(self):
        source_name = self._data_source.get_source_name()
        return f'yfinance.MultiSourceTicker object <{self.ticker}> using {source_name}'

    @property
    def data_source(self) -> DataSourceStrategy:
        """获取当前使用的数据源"""
        return self._data_source

    @property
    def source_name(self) -> str:
        """获取当前数据源名称"""
        return self._data_source.get_source_name()

    # =========================
    # 基础信息接口
    # =========================

    @property
    def info(self) -> Dict:
        """股票基本信息"""
        return self._data_source.get_info()

    @property
    def fast_info(self) -> Dict:
        """快速基本信息"""
        return self._data_source.get_fast_info()

    # =========================
    # 历史数据接口
    # =========================

    def history(self, period: str = "1y", interval: str = "1d", 
               start: Optional[str] = None, end: Optional[str] = None) -> pd.DataFrame:
        """
        获取历史价格数据
        
        Args:
            period: 时间周期（1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, max）
            interval: 数据间隔（1d, 1wk, 1mo）
            start: 开始日期（YYYY-MM-DD）
            end: 结束日期（YYYY-MM-DD）
            
        Returns:
            pd.DataFrame: 历史价格数据
        """
        return self._data_source.get_history(period=period, interval=interval, start=start, end=end)

    @property
    def dividends(self) -> pd.Series:
        """股息数据"""
        return self._data_source.get_dividends()

    @property
    def splits(self) -> pd.Series:
        """股票分割数据"""
        return self._data_source.get_splits()

    @property
    def actions(self) -> pd.DataFrame:
        """公司行动数据（股息+分割）"""
        return self._data_source.get_actions()

    # =========================
    # 财务数据接口
    # =========================

    @property
    def financials(self) -> pd.DataFrame:
        """年度财务数据（利润表）"""
        return self._data_source.get_financials(freq="yearly")

    @property
    def quarterly_financials(self) -> pd.DataFrame:
        """季度财务数据（利润表）"""
        return self._data_source.get_financials(freq="quarterly")

    @property
    def balance_sheet(self) -> pd.DataFrame:
        """年度资产负债表"""
        return self._data_source.get_balance_sheet(freq="yearly")

    @property
    def quarterly_balance_sheet(self) -> pd.DataFrame:
        """季度资产负债表"""
        return self._data_source.get_balance_sheet(freq="quarterly")

    @property
    def cashflow(self) -> pd.DataFrame:
        """年度现金流量表"""
        return self._data_source.get_cash_flow(freq="yearly")

    @property
    def quarterly_cashflow(self) -> pd.DataFrame:
        """季度现金流量表"""
        return self._data_source.get_cash_flow(freq="quarterly")

    @property
    def earnings(self) -> Optional[pd.DataFrame]:
        """年度收益数据"""
        return self._data_source.get_earnings(freq="yearly")

    @property
    def quarterly_earnings(self) -> Optional[pd.DataFrame]:
        """季度收益数据"""
        return self._data_source.get_earnings(freq="quarterly")

    # =========================
    # 持股信息接口
    # =========================

    @property
    def major_holders(self) -> pd.DataFrame:
        """主要持股者信息"""
        return self._data_source.get_major_holders()

    @property
    def institutional_holders(self) -> Optional[pd.DataFrame]:
        """机构持股者信息"""
        return self._data_source.get_institutional_holders()

    @property
    def insider_transactions(self) -> Optional[pd.DataFrame]:
        """内部人员交易信息"""
        return self._data_source.get_insider_transactions()

    @property
    def mutualfund_holders(self) -> Optional[pd.DataFrame]:
        """共同基金持股者信息（仅Yahoo Finance支持）"""
        if hasattr(self._data_source, 'get_mutualfund_holders'):
            return self._data_source.get_mutualfund_holders()
        return None

    # =========================
    # 分析数据接口
    # =========================

    @property
    def recommendations(self) -> Optional[pd.DataFrame]:
        """分析师推荐信息"""
        return self._data_source.get_recommendations()

    @property
    def analyst_price_targets(self) -> Optional[Dict]:
        """分析师目标价信息"""
        return self._data_source.get_analyst_price_targets()

    @property
    def earnings_estimate(self) -> Optional[pd.DataFrame]:
        """收益预估信息"""
        return self._data_source.get_earnings_estimate()

    # =========================
    # 新闻和日历接口
    # =========================

    @property
    def news(self) -> List[Dict]:
        """相关新闻（最近10条）"""
        return self._data_source.get_news(count=10)

    def get_news(self, count: int = 10) -> List[Dict]:
        """
        获取相关新闻
        
        Args:
            count: 新闻数量
            
        Returns:
            List[Dict]: 新闻列表
        """
        return self._data_source.get_news(count=count)

    @property
    def calendar(self) -> Optional[Dict]:
        """财报日历"""
        return self._data_source.get_calendar()

    @property
    def earnings_dates(self) -> Optional[pd.DataFrame]:
        """财报日期"""
        return self._data_source.get_earnings_dates()

    # =========================
    # 其他数据接口
    # =========================

    @property
    def sustainability(self) -> Optional[pd.DataFrame]:
        """可持续性数据"""
        return self._data_source.get_sustainability()

    @property
    def shares(self) -> Optional[pd.DataFrame]:
        """股份信息"""
        return self._data_source.get_shares()

    @property
    def isin(self) -> Optional[str]:
        """ISIN代码"""
        return self._data_source.get_isin()

    # =========================
    # 期权数据（特定于Yahoo Finance）
    # =========================

    def option_chain(self, date=None):
        """
        获取期权链数据
        
        Args:
            date: 到期日（可选）
            
        Returns:
            期权链数据（仅Yahoo Finance支持）
        """
        if hasattr(self._data_source, 'get_options'):
            return self._data_source.get_options(date=date)
        else:
            warnings.warn(f"期权数据不被 {self.source_name} 支持")
            return _namedtuple('Options', ['calls', 'puts', 'underlying'])(
                calls=pd.DataFrame(), 
                puts=pd.DataFrame(), 
                underlying={}
            )

    # =========================
    # 元数据和工具方法
    # =========================

    @property
    def history_metadata(self) -> Dict:
        """历史数据元信息"""
        return self._data_source.get_history_metadata()

    def get_timezone(self) -> str:
        """获取市场时区"""
        return self._data_source.get_timezone()

    def is_market_open(self) -> bool:
        """检查市场是否开放"""
        return self._data_source.is_market_open()

    # =========================
    # 向后兼容方法
    # =========================

    def get_info(self) -> Dict:
        """获取基本信息（向后兼容）"""
        return self.info

    def get_history(self, *args, **kwargs) -> pd.DataFrame:
        """获取历史数据（向后兼容）"""
        return self.history(*args, **kwargs)


# 保持向后兼容的 Ticker 类
class Ticker(TickerBase):
    """
    传统 Ticker 类（向后兼容）
    
    保持与原 yfinance 库的完全兼容性，使用 Yahoo Finance 作为数据源。
    """
    
    def __init__(self, ticker, session=None, proxy=_SENTINEL_):
        if proxy is not _SENTINEL_:
            warnings.warn("Set proxy via new config function: yf.set_config(proxy=proxy)", DeprecationWarning, stacklevel=2)
        super(Ticker, self).__init__(ticker, session=session)
        self._expirations = {}
        self._underlying = {}

    def __repr__(self):
        return f'yfinance.Ticker object <{self.ticker}>'

    # 保持原有的 option_chain 实现
    def _download_options(self, date=None):
        if date is None:
            url = f"{_BASE_URL_}/v7/finance/options/{self.ticker}"
        else:
            url = f"{_BASE_URL_}/v7/finance/options/{self.ticker}?date={date}"

        r = self._data.get(url=url).json()
        if len(r.get('optionChain', {}).get('result', [])) > 0:
            for exp in r['optionChain']['result'][0]['expirationDates']:
                self._expirations[pd.Timestamp(exp, unit='s').strftime('%Y-%m-%d')] = exp

            self._underlying = r['optionChain']['result'][0].get('quote', {})

            opt = r['optionChain']['result'][0].get('options', [])

            return dict(**opt[0], underlying=self._underlying) if len(opt) > 0 else {}
        return {}

    def _options2df(self, opt, tz=None):
        data = pd.DataFrame(opt).reindex(columns=[
            'contractSymbol',
            'lastTradeDate',
            'strike',
            'lastPrice',
            'bid',
            'ask',
            'change',
            'percentChange',
            'volume',
            'openInterest',
            'impliedVolatility',
            'inTheMoney',
            'contractSize',
            'currency'])

        data['lastTradeDate'] = pd.to_datetime(
            data['lastTradeDate'], unit='s', utc=True)
        if tz is not None:
            data['lastTradeDate'] = data['lastTradeDate'].dt.tz_convert(tz)
        return data

    def option_chain(self, date=None, tz=None):
        if date is None:
            options = self._download_options()
        else:
            if not self._expirations:
                self._download_options()
            if date not in self._expirations:
                raise ValueError(
                    f"Expiration `{date}` cannot be found. "
                    f"Available expirations are: [{', '.join(self._expirations)}]")
            date = self._expirations[date]
            options = self._download_options(date)

        if not options:
            return _namedtuple('Options', ['calls', 'puts', 'underlying'])(
                calls=pd.DataFrame(), 
                puts=pd.DataFrame(), 
                underlying={}
            )

        calls = self._options2df(options['calls'], tz)
        puts = self._options2df(options['puts'], tz)

        return _namedtuple('Options', ['calls', 'puts', 'underlying'])(
            calls=calls, 
            puts=puts, 
            underlying=options.get('underlying', {})
        )


# 为了更好的用户体验，提供一个便捷函数
def create_ticker(ticker: str, preferred_source: str = None, **kwargs) -> MultiSourceTicker:
    """
    创建多数据源股票对象
    
    Args:
        ticker: 股票代码
        preferred_source: 首选数据源（'yahoo', 'akshare'）
        **kwargs: 其他参数
        
    Returns:
        MultiSourceTicker: 多数据源股票对象
    """
    return MultiSourceTicker(ticker, preferred_source=preferred_source, **kwargs)
