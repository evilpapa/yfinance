#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Yahoo Finance 数据源适配器

该模块实现了基于 Yahoo Finance 的数据源适配器，用于获取全球金融市场数据。
这是原有 yfinance 功能的重构版本，采用新的数据源架构。
"""

import re
import warnings
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Union
import pandas as pd
import numpy as np

from curl_cffi import requests

from .base import DataSourceStrategy
from .. import utils, cache
from ..data import YfData
from ..exceptions import YFEarningsDateMissing, YFRateLimitError
from ..scrapers.analysis import Analysis
from ..scrapers.fundamentals import Fundamentals
from ..scrapers.holders import Holders
from ..scrapers.quote import Quote, FastInfo
from ..scrapers.history import PriceHistory
from ..scrapers.funds import FundsData
from ..const import _BASE_URL_, _ROOT_URL_, _QUERY1_URL_, _SENTINEL_


class YahooDataSource(DataSourceStrategy):
    """
    Yahoo Finance 数据源适配器
    
    支持全球主要金融市场，包括：
    1. 美股（NYSE, NASDAQ, AMEX）
    2. 港股（HKEX）
    3. 欧洲市场（LSE, EURONEXT, etc.）
    4. 亚洲市场（TSE, SSE, SZSE等）
    5. 其他全球市场
    """

    def __init__(self, ticker: str, session=None):
        """
        初始化 Yahoo Finance 数据源
        
        Args:
            ticker: 股票代码（支持多种格式，如 AAPL, 0700.HK, TSM等）
            session: HTTP会话对象
        """
        super().__init__(ticker)
        self._source_name = "Yahoo Finance"
        self._supported_markets = [
            "US", "HK", "UK", "DE", "FR", "JP", "AU", "CA", "IN", "BR", "CN"
        ]
        
        # 初始化 Yahoo Finance 相关组件
        self.session = session or requests.Session(impersonate="chrome")
        self._tz = None
        self._data: YfData = YfData(session=self.session)
        
        # 懒加载组件
        self._price_history = None
        self._analysis = None
        self._holders = None
        self._quote = None
        self._fundamentals = None
        self._funds_data = None
        self._fast_info = None

    def _validate_ticker(self) -> bool:
        """
        验证股票代码是否为有效的格式
        
        Returns:
            bool: 如果有效则返回 True
            
        Raises:
            ValueError: 如果股票代码无效
        """
        if not self.ticker or self.ticker == "":
            raise ValueError("股票代码不能为空")
        
        # Yahoo Finance 支持多种格式，基本验证
        if len(self.ticker) > 20:  # 合理的长度限制
            raise ValueError(f"股票代码过长: {self.ticker}")
        
        return True

    def supports_ticker(self, ticker: str) -> bool:
        """
        检查是否支持指定的股票代码
        
        Args:
            ticker: 股票代码
            
        Returns:
            bool: 如果支持则返回 True
        """
        try:
            # Yahoo Finance 支持绝大多数格式，除了纯6位数字（A股格式）
            if not ticker or ticker == "":
                return False
            
            # 排除纯6位数字（A股专用格式）
            if re.match(r'^\d{6}$', ticker.strip()):
                return False
            
            return True
        except:
            return False

    def _lazy_load_components(self):
        """懒加载必要的组件"""
        if self._analysis is None:
            self._analysis = Analysis(self._data, self.ticker)
        if self._holders is None:
            self._holders = Holders(self._data, self.ticker)
        if self._quote is None:
            self._quote = Quote(self._data, self.ticker)
        if self._fundamentals is None:
            self._fundamentals = Fundamentals(self._data, self.ticker)

    def _lazy_load_price_history(self):
        """懒加载价格历史组件"""
        if self._price_history is None:
            self._price_history = PriceHistory(self._data, self.ticker, self._get_ticker_tz(timeout=10))
        return self._price_history

    def _get_ticker_tz(self, timeout=10):
        """获取股票市场时区"""
        if self._tz is not None:
            return self._tz
        
        c = cache.get_tz_cache()
        tz = c.lookup(self.ticker)

        if tz and not utils.is_valid_timezone(tz):
            c.store(self.ticker, None)
            tz = None

        if tz is None:
            tz = self._fetch_ticker_tz(timeout)
            if tz is None:
                # 从 info 中获取时区信息
                info = self.get_info()
                for k in ['exchangeTimezoneName', 'timeZoneFullName']:
                    if k in info:
                        tz = info[k]
                        break
            if utils.is_valid_timezone(tz):
                c.store(self.ticker, tz)
            else:
                tz = None

        self._tz = tz
        return tz

    def _fetch_ticker_tz(self, timeout):
        """从 Yahoo Finance 获取时区信息"""
        try:
            params = {"range": "1d", "interval": "1d"}
            url = f"{_BASE_URL_}/v8/finance/chart/{self.ticker}"
            
            response = self._data.get(url=url, params=params, timeout=timeout)
            response.raise_for_status()
            
            data = response.json()
            
            if 'chart' in data and 'result' in data['chart']:
                results = data['chart']['result']
                if results and len(results) > 0:
                    meta = results[0].get('meta', {})
                    return meta.get('exchangeTimezoneName')
            
            return None
        except Exception:
            return None

    # =========================
    # 基础信息接口实现
    # =========================

    def get_info(self) -> Dict:
        """获取股票基本信息"""
        try:
            self._lazy_load_components()
            return self._quote.info
        except Exception as e:
            warnings.warn(f"获取股票信息失败: {e}")
            return {'symbol': self.ticker, 'error': str(e)}

    def get_fast_info(self) -> Dict:
        """获取快速基本信息"""
        try:
            if self._fast_info is None:
                self._fast_info = FastInfo(self._data, self.ticker)
            return self._fast_info.info
        except Exception as e:
            warnings.warn(f"获取快速信息失败: {e}")
            return {'symbol': self.ticker, 'error': str(e)}

    # =========================
    # 历史数据接口实现
    # =========================

    def get_history(self, period: str = "1y", interval: str = "1d", 
                   start: Optional[str] = None, end: Optional[str] = None) -> pd.DataFrame:
        """获取历史价格数据"""
        try:
            return self._lazy_load_price_history().history(
                period=period, 
                interval=interval, 
                start=start, 
                end=end
            )
        except Exception as e:
            warnings.warn(f"获取历史数据失败: {e}")
            return pd.DataFrame()

    def get_dividends(self, period: str = "max") -> pd.Series:
        """获取股息数据"""
        try:
            return self._lazy_load_price_history().dividends
        except Exception as e:
            warnings.warn(f"获取股息数据失败: {e}")
            return pd.Series(dtype=float)

    def get_splits(self, period: str = "max") -> pd.Series:
        """获取股票分割数据"""
        try:
            return self._lazy_load_price_history().splits
        except Exception as e:
            warnings.warn(f"获取分割数据失败: {e}")
            return pd.Series(dtype=float)

    def get_actions(self, period: str = "max") -> pd.DataFrame:
        """获取公司行动数据"""
        try:
            return self._lazy_load_price_history().actions
        except Exception as e:
            warnings.warn(f"获取公司行动数据失败: {e}")
            return pd.DataFrame()

    # =========================
    # 财务数据接口实现
    # =========================

    def get_financials(self, freq: str = "yearly") -> pd.DataFrame:
        """获取财务数据（利润表）"""
        try:
            self._lazy_load_components()
            if freq == "quarterly":
                return self._fundamentals.quarterly_financials
            else:
                return self._fundamentals.financials
        except Exception as e:
            warnings.warn(f"获取财务数据失败: {e}")
            return pd.DataFrame()

    def get_balance_sheet(self, freq: str = "yearly") -> pd.DataFrame:
        """获取资产负债表"""
        try:
            self._lazy_load_components()
            if freq == "quarterly":
                return self._fundamentals.quarterly_balance_sheet
            else:
                return self._fundamentals.balance_sheet
        except Exception as e:
            warnings.warn(f"获取资产负债表失败: {e}")
            return pd.DataFrame()

    def get_cash_flow(self, freq: str = "yearly") -> pd.DataFrame:
        """获取现金流量表"""
        try:
            self._lazy_load_components()
            if freq == "quarterly":
                return self._fundamentals.quarterly_cashflow
            else:
                return self._fundamentals.cashflow
        except Exception as e:
            warnings.warn(f"获取现金流量表失败: {e}")
            return pd.DataFrame()

    def get_earnings(self, freq: str = "yearly") -> Optional[pd.DataFrame]:
        """获取收益数据"""
        try:
            self._lazy_load_components()
            if freq == "quarterly":
                return self._fundamentals.quarterly_earnings
            else:
                return self._fundamentals.earnings
        except Exception as e:
            warnings.warn(f"获取收益数据失败: {e}")
            return None

    # =========================
    # 持股信息接口实现
    # =========================

    def get_major_holders(self) -> pd.DataFrame:
        """获取主要持股者信息"""
        try:
            self._lazy_load_components()
            return self._holders.major_holders
        except Exception as e:
            warnings.warn(f"获取主要持股者信息失败: {e}")
            return pd.DataFrame()

    def get_institutional_holders(self) -> Optional[pd.DataFrame]:
        """获取机构持股者信息"""
        try:
            self._lazy_load_components()
            return self._holders.institutional_holders
        except Exception as e:
            warnings.warn(f"获取机构持股者信息失败: {e}")
            return None

    def get_insider_transactions(self) -> Optional[pd.DataFrame]:
        """获取内部人员交易信息"""
        try:
            self._lazy_load_components()
            return self._holders.insider_transactions
        except Exception as e:
            warnings.warn(f"获取内部人员交易信息失败: {e}")
            return None

    # =========================
    # 分析数据接口实现
    # =========================

    def get_recommendations(self) -> Optional[pd.DataFrame]:
        """获取分析师推荐信息"""
        try:
            self._lazy_load_components()
            return self._analysis.recommendations
        except Exception as e:
            warnings.warn(f"获取分析师推荐信息失败: {e}")
            return None

    def get_analyst_price_targets(self) -> Optional[Dict]:
        """获取分析师目标价信息"""
        try:
            self._lazy_load_components()
            # 从 recommendations 中提取目标价信息
            recommendations = self._analysis.recommendations
            if recommendations is not None and not recommendations.empty:
                # 尝试获取最新的目标价信息
                if 'targetMeanPrice' in recommendations.columns:
                    latest = recommendations.iloc[-1]
                    return {
                        'targetMeanPrice': latest.get('targetMeanPrice'),
                        'targetHighPrice': latest.get('targetHighPrice'),
                        'targetLowPrice': latest.get('targetLowPrice'),
                        'targetMedianPrice': latest.get('targetMedianPrice'),
                    }
            return None
        except Exception as e:
            warnings.warn(f"获取分析师目标价信息失败: {e}")
            return None

    def get_earnings_estimate(self) -> Optional[pd.DataFrame]:
        """获取收益预估信息"""
        try:
            self._lazy_load_components()
            # Yahoo Finance 的收益预估信息通常在分析数据中
            return getattr(self._analysis, 'earnings_estimate', None)
        except Exception as e:
            warnings.warn(f"获取收益预估信息失败: {e}")
            return None

    # =========================
    # 新闻和日历接口实现
    # =========================

    def get_news(self, count: int = 10) -> List[Dict]:
        """获取相关新闻"""
        try:
            self._lazy_load_components()
            # 调用 Yahoo Finance 的新闻接口
            news_data = self._quote.news
            
            if not news_data:
                return []
            
            # 限制数量并标准化格式
            news_list = []
            for news_item in news_data[:count]:
                standardized_news = {
                    'title': news_item.get('title', ''),
                    'summary': news_item.get('summary', ''),
                    'link': news_item.get('link', ''),
                    'published': news_item.get('providerPublishTime', ''),
                    'source': news_item.get('publisher', 'Yahoo Finance'),
                }
                news_list.append(standardized_news)
            
            return news_list
        except Exception as e:
            warnings.warn(f"获取新闻失败: {e}")
            return []

    def get_calendar(self) -> Optional[Dict]:
        """获取财报日历"""
        try:
            self._lazy_load_components()
            # 从基本信息中获取财报相关日期
            info = self.get_info()
            calendar_info = {}
            
            earnings_dates = ['earningsDate', 'exDividendDate', 'dividendDate']
            for date_key in earnings_dates:
                if date_key in info:
                    calendar_info[date_key] = info[date_key]
            
            return calendar_info if calendar_info else None
        except Exception as e:
            warnings.warn(f"获取财报日历失败: {e}")
            return None

    def get_earnings_dates(self, limit: int = 12) -> Optional[pd.DataFrame]:
        """获取财报日期"""
        try:
            # 尝试从缓存或API获取财报日期
            calendar = self.get_calendar()
            if calendar and 'earningsDate' in calendar:
                earnings_dates = calendar['earningsDate']
                if isinstance(earnings_dates, list):
                    df_data = []
                    for date in earnings_dates[:limit]:
                        df_data.append({
                            'Earnings Date': pd.to_datetime(date, unit='s'),
                            'EPS Estimate': None,
                            'Reported EPS': None,
                            'Surprise(%)': None
                        })
                    return pd.DataFrame(df_data)
            
            return None
        except Exception as e:
            warnings.warn(f"获取财报日期失败: {e}")
            return None

    # =========================
    # 其他数据接口实现
    # =========================

    def get_sustainability(self) -> Optional[pd.DataFrame]:
        """获取可持续性数据"""
        try:
            self._lazy_load_components()
            return getattr(self._fundamentals, 'sustainability', None)
        except Exception as e:
            warnings.warn(f"获取可持续性数据失败: {e}")
            return None

    def get_shares(self) -> Optional[pd.DataFrame]:
        """获取股份信息"""
        try:
            info = self.get_info()
            
            if info and any(key in info for key in ['sharesOutstanding', 'floatShares', 'impliedSharesOutstanding']):
                shares_data = {
                    'Total Shares': info.get('sharesOutstanding') or info.get('impliedSharesOutstanding'),
                    'Float Shares': info.get('floatShares'),
                    'Date': pd.Timestamp.now()
                }
                
                return pd.DataFrame([shares_data])
            
            return None
        except Exception as e:
            warnings.warn(f"获取股份信息失败: {e}")
            return None

    def get_isin(self) -> Optional[str]:
        """获取 ISIN 代码"""
        try:
            # 如果ticker本身就是ISIN，直接返回
            if utils.is_isin(self.ticker):
                return self.ticker
            
            # 从基本信息中获取ISIN
            info = self.get_info()
            return info.get('isin') if info else None
        except Exception as e:
            return None

    # =========================
    # 元数据接口实现
    # =========================

    def get_history_metadata(self) -> Dict:
        """获取历史数据元信息"""
        try:
            history_meta = self._lazy_load_price_history()._get_ticker_info()
            
            return {
                'symbol': self.ticker,
                'source': self._source_name,
                'currency': history_meta.get('currency'),
                'exchangeName': history_meta.get('exchangeName'),
                'timezone': history_meta.get('exchangeTimezoneName'),
                'instrumentType': history_meta.get('instrumentType'),
                'firstTradeDate': history_meta.get('firstTradeDate'),
            }
        except Exception as e:
            return {
                'symbol': self.ticker,
                'source': self._source_name,
                'error': str(e)
            }

    def get_source_name(self) -> str:
        """获取数据源名称"""
        return self._source_name

    def get_supported_markets(self) -> List[str]:
        """获取支持的市场列表"""
        return self._supported_markets.copy()

    # =========================
    # 特有功能接口
    # =========================

    def get_options(self, date=None) -> Optional[Dict]:
        """获取期权数据"""
        try:
            # 这个功能特定于 Yahoo Finance，其他数据源可能不支持
            from ..ticker import Ticker  # 避免循环导入
            ticker_obj = Ticker(self.ticker, session=self.session)
            return ticker_obj.option_chain(date=date)
        except Exception as e:
            warnings.warn(f"获取期权数据失败: {e}")
            return None

    def get_mutualfund_holders(self) -> Optional[pd.DataFrame]:
        """获取共同基金持股者信息"""
        try:
            self._lazy_load_components()
            return getattr(self._holders, 'mutualfund_holders', None)
        except Exception as e:
            warnings.warn(f"获取共同基金持股者信息失败: {e}")
            return None

    # =========================
    # 工具方法
    # =========================

    def get_timezone(self) -> str:
        """获取市场时区"""
        tz = self._get_ticker_tz()
        return tz if tz else "UTC"

    def is_market_open(self) -> bool:
        """检查市场是否开放"""
        try:
            # 获取实时数据来判断市场状态
            fast_info = self.get_fast_info()
            
            # 检查是否有最新的交易数据
            if 'regularMarketTime' in fast_info:
                market_time = pd.to_datetime(fast_info['regularMarketTime'], unit='s')
                now = pd.Timestamp.now(tz=self.get_timezone())
                
                # 如果最新交易时间在1小时内，认为市场可能是开放的
                time_diff = now - market_time
                return time_diff.total_seconds() < 3600  # 1小时内
            
            return False
        except Exception:
            return False
