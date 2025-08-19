import pandas as pd
from typing import Dict, Any, Optional
import akshare as ak

from .base import DataSourceStrategy

class AkshareDataSource(DataSourceStrategy):
    """
    akshare 的数据源实现。
    Data source implementation for akshare.

    这个类作为适配器, 调用 akshare 的函数获取数据,
    然后将返回的数据格式转换为 yfinance 的统一格式。
    """

    def get_info(self, ticker: str, proxy: Optional[str] = None, timeout: Optional[int] = None) -> Dict[str, Any]:
        """
        使用 akshare 获取股票的基本信息和实时行情, 并将其适配为 yfinance 的 info 字典格式。
        Uses akshare to fetch basic info and real-time quote, adapting it to yfinance's info dict format.
        """
        try:
            # akshare 使用 6 位数字代码, 无需市场前缀, e.g., "600519"
            symbol = ticker.split('.')[0] if '.' in ticker else ticker
            if not symbol.isdigit() or len(symbol) != 6:
                raise ValueError("Invalid A-share stock code format for akshare.")

            # 获取实时行情数据 (Fetch real-time quote data)
            realtime_df = ak.stock_zh_a_spot_em()
            stock_quote = realtime_df[realtime_df['代码'] == symbol]

            if stock_quote.empty:
                return {'symbol': ticker, 'error': 'No real-time data found in akshare.'}

            # 获取股票基础信息 (Fetch basic stock information)
            basic_info_df = ak.stock_individual_info_em(symbol=symbol)

            # 将两个DataFrame的数据合并和适配 (Combine and adapt data from both DataFrames)
            info = {
                'symbol': ticker,
                'shortName': stock_quote.iloc[0]['名称'],
                'currentPrice': stock_quote.iloc[0]['最新价'],
                'open': stock_quote.iloc[0]['今开'],
                'high': stock_quote.iloc[0]['最高'],
                'low': stock_quote.iloc[0]['最低'],
                'previousClose': stock_quote.iloc[0]['昨收'],
                'volume': stock_quote.iloc[0]['成交量'],
                'turnover': stock_quote.iloc[0]['成交额'],
                'turnoverRate': stock_quote.iloc[0]['换手率'],
                'peRatio': stock_quote.iloc[0]['市盈率-动态'],
                'pbRatio': stock_quote.iloc[0]['市净率'],
                'marketCap': stock_quote.iloc[0]['总市值'],
                'currency': 'CNY'
            }

            # 添加基础信息 (Add basic information)
            if not basic_info_df.empty:
                basic_info_dict = dict(zip(basic_info_df['item'], basic_info_df['value']))
                info['industry'] = basic_info_dict.get('行业')
                info['longBusinessSummary'] = basic_info_dict.get('主营业务')

            return info

        except Exception as e:
            return {'symbol': ticker, 'error': str(e)}

    def get_history(self, ticker: str, period: str = 'daily',
                    start: Optional[str] = '19700101', end: Optional[str] = '22220101',
                    **kwargs) -> Optional[pd.DataFrame]:
        """
        使用 akshare 获取历史行情数据。
        akshare 的返回格式与 yfinance 非常相似, 适配工作量较小。
        Uses akshare to fetch historical price data. The format is similar to yfinance.
        """
        try:
            symbol = ticker.split('.')[0] if '.' in ticker else ticker
            if not symbol.isdigit() or len(symbol) != 6:
                raise ValueError("Invalid A-share stock code format for akshare.")

            # akshare 的周期参数映射 (Map yfinance interval to akshare period)
            period_map = {'1d': 'daily', '1wk': 'weekly', '1mo': 'monthly'}
            ak_period = period_map.get(kwargs.get('interval', '1d'), 'daily')

            # yfinance start/end format is 'YYYY-MM-DD', akshare is 'YYYYMMDD'
            start_dt = start.replace('-', '') if start else '19700101'
            end_dt = end.replace('-', '') if end else '22220101'

            df = ak.stock_zh_a_hist(symbol=symbol, period=ak_period, start_date=start_dt, end_date=end_dt, adjust="qfq")

            if df.empty:
                return None

            # 重命名字段以匹配 yfinance (Rename columns to match yfinance)
            df.rename(columns={
                '日期': 'Date',
                '开盘': 'Open',
                '最高': 'High',
                '最低': 'Low',
                '收盘': 'Close',
                '成交量': 'Volume'
            }, inplace=True)
            df.set_index('Date', inplace=True)
            df.index = pd.to_datetime(df.index)

            # yfinance expects 'Adj Close' column
            if 'Adj Close' not in df.columns:
                df['Adj Close'] = df['Close']

            return df[['Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']]
        except Exception:
            return None

    # 其他方法暂未实现 (Other methods not implemented yet)
    def get_income_stmt(self, ticker: str, **kwargs) -> Optional[pd.DataFrame]:
        raise NotImplementedError("Financials have not been migrated to AkshareDataSource yet.")

    def get_balance_sheet(self, ticker: str, **kwargs) -> Optional[pd.DataFrame]:
        raise NotImplementedError("Financials have not been migrated to AkshareDataSource yet.")

    def get_cash_flow(self, ticker: str, **kwargs) -> Optional[pd.DataFrame]:
        raise NotImplementedError("Financials have not been migrated to AkshareDataSource yet.")
