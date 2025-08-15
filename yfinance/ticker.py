#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# yfinance - market data downloader
# https://github.com/ranaroussi/yfinance
#
# Copyright 2017-2019 Ran Aroussi
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

from __future__ import print_function

from collections import namedtuple as _namedtuple
import warnings

import pandas as _pd

from .base import TickerBase
from .const import _BASE_URL_, _SENTINEL_
from .scrapers.funds import FundsData


class Ticker(TickerBase):
    """
    Ticker类，是与特定股票代码交互的主要入口点。
    它继承自TickerBase，并提供了一组丰富的属性来访问各种财务数据。
    """
    def __init__(self, ticker, session=None, proxy=_SENTINEL_):
        if proxy is not _SENTINEL_:
            warnings.warn("Set proxy via new config function: yf.set_config(proxy=proxy)", DeprecationWarning, stacklevel=2)
            self._data._set_proxy(proxy)
        super(Ticker, self).__init__(ticker, session=session)
        self._expirations = {}
        self._underlying  = {}

    def __repr__(self):
        return f'yfinance.Ticker object <{self.ticker}>'

    def _download_options(self, date=None):
        """下载期权数据"""
        if date is None:
            url = f"{_BASE_URL_}/v7/finance/options/{self.ticker}"
        else:
            url = f"{_BASE_URL_}/v7/finance/options/{self.ticker}?date={date}"

        r = self._data.get(url=url).json()
        if len(r.get('optionChain', {}).get('result', [])) > 0:
            for exp in r['optionChain']['result'][0]['expirationDates']:
                self._expirations[_pd.Timestamp(exp, unit='s').strftime('%Y-%m-%d')] = exp

            self._underlying = r['optionChain']['result'][0].get('quote', {})

            opt = r['optionChain']['result'][0].get('options', [])

            return dict(**opt[0],underlying=self._underlying) if len(opt) > 0 else {}
        return {}

    def _options2df(self, opt, tz=None):
        """将期权数据转换为DataFrame"""
        data = _pd.DataFrame(opt).reindex(columns=[
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

        data['lastTradeDate'] = _pd.to_datetime(
            data['lastTradeDate'], unit='s', utc=True)
        if tz is not None:
            data['lastTradeDate'] = data['lastTradeDate'].dt.tz_convert(tz)
        return data

    def option_chain(self, date=None, tz=None):
        """获取期权链"""
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
            return _namedtuple('Options', ['calls', 'puts', 'underlying'])(**{
                "calls": None, "puts": None, "underlying": None
            })

        return _namedtuple('Options', ['calls', 'puts', 'underlying'])(**{
            "calls": self._options2df(options['calls'], tz=tz),
            "puts": self._options2df(options['puts'], tz=tz),
            "underlying": options['underlying']
        })

    @property
    def isin(self):
        """ISIN码"""
        return self.get_isin()

    @property
    def major_holders(self) -> _pd.DataFrame:
        """主要股东"""
        return self.get_major_holders()

    @property
    def institutional_holders(self) -> _pd.DataFrame:
        """机构股东"""
        return self.get_institutional_holders()

    @property
    def mutualfund_holders(self) -> _pd.DataFrame:
        """共同基金股东"""
        return self.get_mutualfund_holders()

    @property
    def insider_purchases(self) -> _pd.DataFrame:
        """内部人士购买"""
        return self.get_insider_purchases()

    @property
    def insider_transactions(self) -> _pd.DataFrame:
        """内部人士交易"""
        return self.get_insider_transactions()

    @property
    def insider_roster_holders(self) -> _pd.DataFrame:
        """内部人士名册"""
        return self.get_insider_roster_holders()

    @property
    def dividends(self) -> _pd.Series:
        """股息"""
        return self.get_dividends()

    @property
    def capital_gains(self) -> _pd.Series:
        """资本利得"""
        return self.get_capital_gains()

    @property
    def splits(self) -> _pd.Series:
        """股票拆分"""
        return self.get_splits()

    @property
    def actions(self) -> _pd.DataFrame:
        """公司行动"""
        return self.get_actions()

    @property
    def shares(self) -> _pd.DataFrame:
        """股票份额"""
        return self.get_shares()

    @property
    def info(self) -> dict:
        """公司信息"""
        return self.get_info()

    @property
    def fast_info(self):
        """快速信息"""
        return self.get_fast_info()

    @property
    def calendar(self) -> dict:
        """日历事件"""
        return self.get_calendar()

    @property
    def sec_filings(self) -> dict:
        """SEC文件"""
        return self.get_sec_filings()

    @property
    def recommendations(self):
        """分析师建议"""
        return self.get_recommendations()

    @property
    def recommendations_summary(self):
        """分析师建议摘要"""
        return self.get_recommendations_summary()

    @property
    def upgrades_downgrades(self):
        """评级升降级"""
        return self.get_upgrades_downgrades()

    @property
    def earnings(self) -> _pd.DataFrame:
        """盈利"""
        return self.get_earnings()

    @property
    def quarterly_earnings(self) -> _pd.DataFrame:
        """季度盈利"""
        return self.get_earnings(freq='quarterly')

    @property
    def income_stmt(self) -> _pd.DataFrame:
        """损益表"""
        return self.get_income_stmt(pretty=True)

    @property
    def quarterly_income_stmt(self) -> _pd.DataFrame:
        """季度损益表"""
        return self.get_income_stmt(pretty=True, freq='quarterly')

    @property
    def ttm_income_stmt(self) -> _pd.DataFrame:
        """滚动十二个月损益表"""
        return self.get_income_stmt(pretty=True, freq='trailing')

    @property
    def incomestmt(self) -> _pd.DataFrame:
        return self.income_stmt

    @property
    def quarterly_incomestmt(self) -> _pd.DataFrame:
        return self.quarterly_income_stmt

    @property
    def ttm_incomestmt(self) -> _pd.DataFrame:
        return self.ttm_income_stmt

    @property
    def financials(self) -> _pd.DataFrame:
        return self.income_stmt

    @property
    def quarterly_financials(self) -> _pd.DataFrame:
        return self.quarterly_income_stmt

    @property
    def ttm_financials(self) -> _pd.DataFrame:
        return self.ttm_income_stmt

    @property
    def balance_sheet(self) -> _pd.DataFrame:
        """资产负债表"""
        return self.get_balance_sheet(pretty=True)

    @property
    def quarterly_balance_sheet(self) -> _pd.DataFrame:
        """季度资产负债表"""
        return self.get_balance_sheet(pretty=True, freq='quarterly')

    @property
    def balancesheet(self) -> _pd.DataFrame:
        return self.balance_sheet

    @property
    def quarterly_balancesheet(self) -> _pd.DataFrame:
        return self.quarterly_balance_sheet

    @property
    def cash_flow(self) -> _pd.DataFrame:
        """现金流量表"""
        return self.get_cash_flow(pretty=True, freq="yearly")

    @property
    def quarterly_cash_flow(self) -> _pd.DataFrame:
        """季度现金流量表"""
        return self.get_cash_flow(pretty=True, freq='quarterly')

    @property
    def ttm_cash_flow(self) -> _pd.DataFrame:
        """滚动十二个月现金流量表"""
        return self.get_cash_flow(pretty=True, freq='trailing')

    @property
    def cashflow(self) -> _pd.DataFrame:
        return self.cash_flow

    @property
    def quarterly_cashflow(self) -> _pd.DataFrame:
        return self.quarterly_cash_flow

    @property
    def ttm_cashflow(self) -> _pd.DataFrame:
        return self.ttm_cash_flow

    @property
    def analyst_price_targets(self) -> dict:
        """分析师目标价"""
        return self.get_analyst_price_targets()

    @property
    def earnings_estimate(self) -> _pd.DataFrame:
        """盈利预测"""
        return self.get_earnings_estimate()

    @property
    def revenue_estimate(self) -> _pd.DataFrame:
        """收入预测"""
        return self.get_revenue_estimate()

    @property
    def earnings_history(self) -> _pd.DataFrame:
        """盈利历史"""
        return self.get_earnings_history()

    @property
    def eps_trend(self) -> _pd.DataFrame:
        """每股收益趋势"""
        return self.get_eps_trend()

    @property
    def eps_revisions(self) -> _pd.DataFrame:
        """每股收益修正"""
        return self.get_eps_revisions()

    @property
    def growth_estimates(self) -> _pd.DataFrame:
        """增长预测"""
        return self.get_growth_estimates()

    @property
    def sustainability(self) -> _pd.DataFrame:
        """可持续性"""
        return self.get_sustainability()

    @property
    def options(self) -> tuple:
        """期权到期日"""
        if not self._expirations:
            self._download_options()
        return tuple(self._expirations.keys())

    @property
    def news(self) -> list:
        """新闻"""
        return self.get_news()

    @property
    def earnings_dates(self) -> _pd.DataFrame:
        """财报日期"""
        return self.get_earnings_dates()

    @property
    def history_metadata(self) -> dict:
        """历史元数据"""
        return self.get_history_metadata()

    @property
    def funds_data(self) -> FundsData:
        """基金数据"""
        return self.get_funds_data()
