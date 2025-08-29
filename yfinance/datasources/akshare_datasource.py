#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
AKShare 数据源适配器

该模块实现了基于 AKShare 的数据源适配器，专门用于获取中国A股市场数据。
将 AKShare 的数据格式转换为 yfinance 兼容的标准格式。
"""

import re
import warnings
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Union
import pandas as pd
import numpy as np

try:
    import akshare as ak
except ImportError:
    ak = None
    warnings.warn("AKShare 未安装，AkshareDataSource 将不可用", UserWarning)

from .base import DataSourceStrategy


class AkshareDataSource(DataSourceStrategy):
    """
    AKShare 数据源适配器
    
    专门用于获取中国A股市场数据，支持：
    1. 上海证券交易所（SSE）股票
    2. 深圳证券交易所（SZSE）股票
    3. 北京证券交易所（BSE）股票
    4. 科创板和创业板股票
    """

    def __init__(self, ticker: str):
        """
        初始化 AKShare 数据源
        
        Args:
            ticker: 股票代码（支持 6 位数字格式）
        """
        if ak is None:
            raise ImportError("使用 AkshareDataSource 需要安装 akshare: pip install akshare")
        
        super().__init__(ticker)
        self._source_name = "AKShare"
        self._supported_markets = ["上海证券交易所", "深圳证券交易所", "北京证券交易所"]

    def _validate_ticker(self) -> bool:
        """
        验证股票代码是否为有效的中国A股代码
        
        Returns:
            bool: 如果有效则返回 True
            
        Raises:
            ValueError: 如果股票代码无效
        """
        # 中国A股代码模式：6位数字
        if not re.match(r'^\d{6}$', self.ticker):
            raise ValueError(f"无效的中国A股代码: {self.ticker}. 期望6位数字格式")
        
        # 检查代码范围
        code_num = int(self.ticker)
        valid_ranges = [
            (1, 999999),      # 全范围，具体验证由交易所规则决定
        ]
        
        if not any(start <= code_num <= end for start, end in valid_ranges):
            raise ValueError(f"股票代码 {self.ticker} 超出有效范围")
        
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
            # 临时创建实例来验证
            temp_ticker = ticker.upper().strip()
            return bool(re.match(r'^\d{6}$', temp_ticker))
        except:
            return False

    def _format_date(self, date_str: str) -> str:
        """
        格式化日期为 AKShare 期望的格式 (YYYYMMDD)
        
        Args:
            date_str: 日期字符串 (YYYY-MM-DD 或其他格式)
            
        Returns:
            str: 格式化后的日期字符串
        """
        if not date_str:
            return ""
        
        try:
            # 尝试解析日期
            if isinstance(date_str, str):
                if "-" in date_str:
                    # YYYY-MM-DD 格式
                    return date_str.replace("-", "")
                elif len(date_str) == 8 and date_str.isdigit():
                    # 已经是 YYYYMMDD 格式
                    return date_str
            
            # 尝试解析为 datetime 对象
            dt = pd.to_datetime(date_str)
            return dt.strftime("%Y%m%d")
        except:
            return ""

    def _standardize_columns(self, df: pd.DataFrame, column_mapping: Dict[str, str]) -> pd.DataFrame:
        """
        标准化列名为 yfinance 格式
        
        Args:
            df: 原始数据框
            column_mapping: 列名映射字典
            
        Returns:
            pd.DataFrame: 标准化后的数据框
        """
        if df is None or df.empty:
            return df
        
        # 重命名列
        df_copy = df.copy()
        df_copy = df_copy.rename(columns=column_mapping)
        
        # 确保必要的列存在
        required_columns = list(column_mapping.values())
        for col in required_columns:
            if col not in df_copy.columns:
                df_copy[col] = np.nan
        
        return df_copy[required_columns]

    # =========================
    # 基础信息接口实现
    # =========================

    def get_info(self) -> Dict:
        """获取股票基本信息"""
        try:
            # 获取股票基本信息
            info_df = ak.stock_individual_info_em(symbol=self.ticker)
            
            # 转换为字典格式
            info_dict = {}
            if info_df is not None and not info_df.empty:
                for _, row in info_df.iterrows():
                    item = row['item']
                    value = row['value']
                    info_dict[item] = value
            
            # 标准化为 yfinance 格式
            standardized_info = {
                'symbol': self.ticker,
                'longName': info_dict.get('股票简称', ''),
                'shortName': info_dict.get('股票简称', ''),
                'currency': 'CNY',
                'exchange': self._get_exchange_name(),
                'country': 'China',
                'marketCap': self._safe_float(info_dict.get('总市值')),
                'totalShares': self._safe_float(info_dict.get('总股本')),
                'floatShares': self._safe_float(info_dict.get('流通股')),
                'currentPrice': self._safe_float(info_dict.get('最新')),
                'previousClose': self._safe_float(info_dict.get('昨收')),
                'industry': info_dict.get('行业', ''),
                'sector': info_dict.get('板块', ''),
            }
            
            # 添加原始数据
            standardized_info['_raw_data'] = info_dict
            
            return standardized_info
            
        except Exception as e:
            warnings.warn(f"获取股票信息失败: {e}")
            return {
                'symbol': self.ticker,
                'error': str(e),
                'currency': 'CNY',
                'exchange': self._get_exchange_name(),
                'country': 'China',
            }

    def get_fast_info(self) -> Dict:
        """获取快速基本信息"""
        try:
            # 获取实时数据
            realtime_df = ak.stock_zh_a_spot_em()
            
            # 查找对应股票
            stock_data = realtime_df[realtime_df['代码'] == self.ticker]
            
            if stock_data.empty:
                return {'symbol': self.ticker, 'error': '未找到实时数据'}
            
            row = stock_data.iloc[0]
            
            return {
                'symbol': self.ticker,
                'lastPrice': self._safe_float(row.get('最新价')),
                'previousClose': self._safe_float(row.get('昨收')),
                'open': self._safe_float(row.get('今开')),
                'dayHigh': self._safe_float(row.get('最高')),
                'dayLow': self._safe_float(row.get('最低')),
                'volume': self._safe_int(row.get('成交量')),
                'marketCap': self._safe_float(row.get('总市值')),
                'currency': 'CNY',
                'exchange': self._get_exchange_name(),
            }
            
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
            # 处理日期参数
            if start is None and end is None:
                # 根据 period 计算开始和结束日期
                end_date = datetime.now()
                if period == "1d":
                    start_date = end_date - timedelta(days=1)
                elif period == "5d":
                    start_date = end_date - timedelta(days=5)
                elif period == "1mo":
                    start_date = end_date - timedelta(days=30)
                elif period == "3mo":
                    start_date = end_date - timedelta(days=90)
                elif period == "6mo":
                    start_date = end_date - timedelta(days=180)
                elif period == "1y":
                    start_date = end_date - timedelta(days=365)
                elif period == "2y":
                    start_date = end_date - timedelta(days=730)
                elif period == "5y":
                    start_date = end_date - timedelta(days=1825)
                elif period == "max":
                    start_date = datetime(1990, 1, 1)  # A股历史开始
                else:
                    start_date = end_date - timedelta(days=365)  # 默认1年
            else:
                start_date = pd.to_datetime(start) if start else datetime(1990, 1, 1)
                end_date = pd.to_datetime(end) if end else datetime.now()
            
            # 格式化日期
            start_str = self._format_date(start_date.strftime("%Y-%m-%d"))
            end_str = self._format_date(end_date.strftime("%Y-%m-%d"))
            
            # 映射间隔
            period_map = {
                "1d": "daily",
                "1wk": "weekly", 
                "1mo": "monthly",
            }
            ak_period = period_map.get(interval, "daily")
            
            # 获取历史数据
            hist_df = ak.stock_zh_a_hist(
                symbol=self.ticker, 
                period=ak_period,
                start_date=start_str,
                end_date=end_str,
                adjust=""  # 不复权
            )
            
            if hist_df is None or hist_df.empty:
                return pd.DataFrame()
            
            # 标准化列名
            column_mapping = {
                '日期': 'Date',
                '开盘': 'Open',
                '收盘': 'Close', 
                '最高': 'High',
                '最低': 'Low',
                '成交量': 'Volume',
                '成交额': 'Amount',
            }
            
            standardized_df = self._standardize_columns(hist_df, column_mapping)
            
            # 设置索引
            standardized_df['Date'] = pd.to_datetime(standardized_df['Date'])
            standardized_df.set_index('Date', inplace=True)
            
            # 添加 Adj Close 列（A股通常不需要复权，直接复制 Close）
            standardized_df['Adj Close'] = standardized_df['Close']
            
            # 重新排序列
            final_columns = ['Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']
            available_columns = [col for col in final_columns if col in standardized_df.columns]
            
            return standardized_df[available_columns]
            
        except Exception as e:
            warnings.warn(f"获取历史数据失败: {e}")
            return pd.DataFrame()

    def get_dividends(self, period: str = "max") -> pd.Series:
        """获取股息数据"""
        try:
            # 获取分红配股数据
            dividend_df = ak.stock_zh_a_dividend_detail(symbol=self.ticker)
            
            if dividend_df is None or dividend_df.empty:
                return pd.Series(dtype=float)
            
            # 筛选分红数据（排除送股等其他操作）
            dividend_df = dividend_df[dividend_df['分红'].notna() & (dividend_df['分红'] > 0)]
            
            if dividend_df.empty:
                return pd.Series(dtype=float)
            
            # 转换为 Series
            dividend_df['日期'] = pd.to_datetime(dividend_df['日期'])
            dividend_series = pd.Series(
                data=dividend_df['分红'].values,
                index=dividend_df['日期'],
                name='Dividends'
            )
            
            return dividend_series.sort_index()
            
        except Exception as e:
            warnings.warn(f"获取分红数据失败: {e}")
            return pd.Series(dtype=float)

    def get_splits(self, period: str = "max") -> pd.Series:
        """获取股票分割数据"""
        try:
            # 获取送股数据
            split_df = ak.stock_zh_a_dividend_detail(symbol=self.ticker)
            
            if split_df is None or split_df.empty:
                return pd.Series(dtype=float)
            
            # 筛选送股数据
            split_df = split_df[split_df['送股'].notna() & (split_df['送股'] > 0)]
            
            if split_df.empty:
                return pd.Series(dtype=float)
            
            # 计算分割比例（送股比例 + 1，因为送股是在原有基础上增加）
            split_df['分割比例'] = (split_df['送股'] / 10) + 1  # 送股通常以每10股为单位
            
            # 转换为 Series
            split_df['日期'] = pd.to_datetime(split_df['日期'])
            split_series = pd.Series(
                data=split_df['分割比例'].values,
                index=split_df['日期'],
                name='Stock Splits'
            )
            
            return split_series.sort_index()
            
        except Exception as e:
            warnings.warn(f"获取分割数据失败: {e}")
            return pd.Series(dtype=float)

    def get_actions(self, period: str = "max") -> pd.DataFrame:
        """获取公司行动数据"""
        try:
            # 合并股息和分割数据
            dividends = self.get_dividends(period)
            splits = self.get_splits(period)
            
            # 创建综合的 actions DataFrame
            actions_data = []
            
            # 添加股息
            for date, dividend in dividends.items():
                actions_data.append({
                    'Date': date,
                    'Dividends': dividend,
                    'Stock Splits': np.nan
                })
            
            # 添加分割
            for date, split in splits.items():
                actions_data.append({
                    'Date': date,
                    'Dividends': np.nan,
                    'Stock Splits': split
                })
            
            if not actions_data:
                return pd.DataFrame(columns=['Dividends', 'Stock Splits'])
            
            actions_df = pd.DataFrame(actions_data)
            actions_df['Date'] = pd.to_datetime(actions_df['Date'])
            actions_df.set_index('Date', inplace=True)
            
            # 按日期分组，合并同一日期的多个操作
            actions_df = actions_df.groupby(actions_df.index).agg({
                'Dividends': 'sum',
                'Stock Splits': 'first'
            })
            
            return actions_df.sort_index()
            
        except Exception as e:
            warnings.warn(f"获取公司行动数据失败: {e}")
            return pd.DataFrame(columns=['Dividends', 'Stock Splits'])

    # =========================
    # 财务数据接口实现
    # =========================

    def get_financials(self, freq: str = "yearly") -> pd.DataFrame:
        """获取财务数据（利润表）"""
        try:
            # 获取利润表数据
            financial_df = ak.stock_financial_abstract_ths(symbol=self.ticker, indicator="利润表")
            
            if financial_df is None or financial_df.empty:
                return pd.DataFrame()
            
            # 转换报告期为日期索引
            financial_df['报告期'] = pd.to_datetime(financial_df['报告期'])
            financial_df.set_index('报告期', inplace=True)
            
            # 筛选频率
            if freq == "quarterly":
                # 保留所有季度数据
                pass
            elif freq == "yearly":
                # 只保留年度数据（12月31日）
                financial_df = financial_df[financial_df.index.month == 12]
            
            return financial_df.sort_index()
            
        except Exception as e:
            warnings.warn(f"获取财务数据失败: {e}")
            return pd.DataFrame()

    def get_balance_sheet(self, freq: str = "yearly") -> pd.DataFrame:
        """获取资产负债表"""
        try:
            # 获取资产负债表数据
            balance_df = ak.stock_financial_abstract_ths(symbol=self.ticker, indicator="资产负债表")
            
            if balance_df is None or balance_df.empty:
                return pd.DataFrame()
            
            # 转换报告期为日期索引
            balance_df['报告期'] = pd.to_datetime(balance_df['报告期'])
            balance_df.set_index('报告期', inplace=True)
            
            # 筛选频率
            if freq == "quarterly":
                pass
            elif freq == "yearly":
                balance_df = balance_df[balance_df.index.month == 12]
            
            return balance_df.sort_index()
            
        except Exception as e:
            warnings.warn(f"获取资产负债表失败: {e}")
            return pd.DataFrame()

    def get_cash_flow(self, freq: str = "yearly") -> pd.DataFrame:
        """获取现金流量表"""
        try:
            # 获取现金流量表数据
            cashflow_df = ak.stock_financial_abstract_ths(symbol=self.ticker, indicator="现金流量表")
            
            if cashflow_df is None or cashflow_df.empty:
                return pd.DataFrame()
            
            # 转换报告期为日期索引
            cashflow_df['报告期'] = pd.to_datetime(cashflow_df['报告期'])
            cashflow_df.set_index('报告期', inplace=True)
            
            # 筛选频率
            if freq == "quarterly":
                pass
            elif freq == "yearly":
                cashflow_df = cashflow_df[cashflow_df.index.month == 12]
            
            return cashflow_df.sort_index()
            
        except Exception as e:
            warnings.warn(f"获取现金流量表失败: {e}")
            return pd.DataFrame()

    def get_earnings(self, freq: str = "yearly") -> Optional[pd.DataFrame]:
        """获取收益数据"""
        try:
            # 从利润表中提取收益信息
            financials = self.get_financials(freq)
            
            if financials.empty:
                return None
            
            # 提取关键收益指标
            earnings_columns = ['净利润', '基本每股收益', '营业总收入']
            available_columns = [col for col in earnings_columns if col in financials.columns]
            
            if not available_columns:
                return None
            
            earnings_df = financials[available_columns].copy()
            
            # 重命名列为英文
            column_mapping = {
                '净利润': 'Net Income',
                '基本每股收益': 'Basic EPS',
                '营业总收入': 'Total Revenue'
            }
            
            earnings_df = earnings_df.rename(columns=column_mapping)
            
            return earnings_df
            
        except Exception as e:
            warnings.warn(f"获取收益数据失败: {e}")
            return None

    # =========================
    # 持股信息接口实现
    # =========================

    def get_major_holders(self) -> pd.DataFrame:
        """获取主要持股者信息"""
        try:
            # 获取股东持股信息
            holders_df = ak.stock_zh_a_gdhs(symbol=self.ticker)
            
            if holders_df is None or holders_df.empty:
                return pd.DataFrame()
            
            return holders_df
            
        except Exception as e:
            warnings.warn(f"获取主要持股者信息失败: {e}")
            return pd.DataFrame()

    def get_institutional_holders(self) -> Optional[pd.DataFrame]:
        """获取机构持股者信息"""
        try:
            # 尝试获取机构持股信息
            # 注意：AKShare 的机构持股数据可能有限
            holders_df = self.get_major_holders()
            
            if holders_df.empty:
                return None
            
            # 尝试筛选机构投资者（基金、保险、社保等）
            institutional_keywords = ['基金', '保险', '社保', '券商', '信托', 'QFII']
            
            if '股东名称' in holders_df.columns:
                mask = holders_df['股东名称'].str.contains('|'.join(institutional_keywords), na=False)
                institutional_df = holders_df[mask]
                
                if not institutional_df.empty:
                    return institutional_df
            
            return None
            
        except Exception as e:
            warnings.warn(f"获取机构持股者信息失败: {e}")
            return None

    def get_insider_transactions(self) -> Optional[pd.DataFrame]:
        """获取内部人员交易信息"""
        # AKShare 暂时不提供内部人员交易的详细数据
        warnings.warn("AKShare 暂不支持内部人员交易数据")
        return None

    # =========================
    # 分析数据接口实现
    # =========================

    def get_recommendations(self) -> Optional[pd.DataFrame]:
        """获取分析师推荐信息"""
        # AKShare 暂时不提供分析师推荐数据
        warnings.warn("AKShare 暂不支持分析师推荐数据")
        return None

    def get_analyst_price_targets(self) -> Optional[Dict]:
        """获取分析师目标价信息"""
        # AKShare 暂时不提供分析师目标价数据
        warnings.warn("AKShare 暂不支持分析师目标价数据")
        return None

    def get_earnings_estimate(self) -> Optional[pd.DataFrame]:
        """获取收益预估信息"""
        # AKShare 暂时不提供收益预估数据
        warnings.warn("AKShare 暂不支持收益预估数据")
        return None

    # =========================
    # 新闻和日历接口实现
    # =========================

    def get_news(self, count: int = 10) -> List[Dict]:
        """获取相关新闻"""
        try:
            # 获取股票新闻
            news_df = ak.stock_news_em(symbol=self.ticker)
            
            if news_df is None or news_df.empty:
                return []
            
            # 限制数量
            news_df = news_df.head(count)
            
            # 转换为标准格式
            news_list = []
            for _, row in news_df.iterrows():
                news_item = {
                    'title': row.get('新闻标题', ''),
                    'summary': row.get('新闻内容', '')[:200] + '...' if len(str(row.get('新闻内容', ''))) > 200 else row.get('新闻内容', ''),
                    'link': row.get('新闻链接', ''),
                    'published': row.get('发布时间', ''),
                    'source': row.get('文章来源', 'AKShare'),
                }
                news_list.append(news_item)
            
            return news_list
            
        except Exception as e:
            warnings.warn(f"获取新闻失败: {e}")
            return []

    def get_calendar(self) -> Optional[Dict]:
        """获取财报日历"""
        # AKShare 暂时不提供财报日历的专门接口
        warnings.warn("AKShare 暂不支持财报日历数据")
        return None

    def get_earnings_dates(self, limit: int = 12) -> Optional[pd.DataFrame]:
        """获取财报日期"""
        # AKShare 暂时不提供财报日期的专门接口
        warnings.warn("AKShare 暂不支持财报日期数据")
        return None

    # =========================
    # 其他数据接口实现
    # =========================

    def get_sustainability(self) -> Optional[pd.DataFrame]:
        """获取可持续性数据"""
        # AKShare 暂时不提供可持续性数据
        warnings.warn("AKShare 暂不支持可持续性数据")
        return None

    def get_shares(self) -> Optional[pd.DataFrame]:
        """获取股份信息"""
        try:
            # 从基本信息中获取股本信息
            info = self.get_info()
            
            if 'totalShares' in info or 'floatShares' in info:
                shares_data = {
                    'Total Shares': info.get('totalShares'),
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
        # A股一般不使用 ISIN 代码，返回 None
        return None

    # =========================
    # 元数据接口实现
    # =========================

    def get_history_metadata(self) -> Dict:
        """获取历史数据元信息"""
        return {
            'symbol': self.ticker,
            'source': self._source_name,
            'currency': 'CNY',
            'exchangeName': self._get_exchange_name(),
            'timezone': 'Asia/Shanghai',
            'instrumentType': 'EQUITY',
            'firstTradeDate': None,  # AKShare 不提供首次交易日期
        }

    def get_source_name(self) -> str:
        """获取数据源名称"""
        return self._source_name

    def get_supported_markets(self) -> List[str]:
        """获取支持的市场列表"""
        return self._supported_markets.copy()

    # =========================
    # 工具方法
    # =========================

    def _get_exchange_name(self) -> str:
        """根据股票代码获取交易所名称"""
        code = self.ticker
        
        if code.startswith('60'):
            return '上海证券交易所'
        elif code.startswith('00') or code.startswith('30'):
            return '深圳证券交易所'
        elif code.startswith('68'):
            return '上海证券交易所-科创板'
        elif code.startswith('8') or code.startswith('4'):
            return '北京证券交易所'
        else:
            return '未知交易所'

    def _safe_float(self, value) -> Optional[float]:
        """安全转换为浮点数"""
        if value is None or value == '':
            return None
        try:
            # 处理中文数值单位
            if isinstance(value, str):
                value = value.replace('万', '').replace('亿', '').replace(',', '')
                if '万' in str(value):
                    value = float(value.replace('万', '')) * 10000
                elif '亿' in str(value):
                    value = float(value.replace('亿', '')) * 100000000
            return float(value)
        except (ValueError, TypeError):
            return None

    def _safe_int(self, value) -> Optional[int]:
        """安全转换为整数"""
        float_val = self._safe_float(value)
        return int(float_val) if float_val is not None else None

    def get_timezone(self) -> str:
        """获取市场时区"""
        return "Asia/Shanghai"

    def is_market_open(self) -> bool:
        """检查A股市场是否开放"""
        # 简化实现：周一到周五，上午9:30-11:30，下午13:00-15:00
        import datetime
        now = datetime.datetime.now()
        
        # 检查是否为工作日
        if now.weekday() >= 5:  # 周六、周日
            return False
        
        # 检查是否在交易时间内
        current_time = now.time()
        morning_start = datetime.time(9, 30)
        morning_end = datetime.time(11, 30)
        afternoon_start = datetime.time(13, 0)
        afternoon_end = datetime.time(15, 0)
        
        return (morning_start <= current_time <= morning_end) or \
               (afternoon_start <= current_time <= afternoon_end)
