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

import warnings
from typing import Union, Optional

import pandas as pd

from . import utils
from .const import _SENTINEL_
from .datasources.factory import DataSourceFactory
from .scrapers.funds import FundsData

_tz_info_fetch_ctr = 0

class TickerBase:
    def __init__(self, ticker, session=None, proxy=_SENTINEL_):
        self.ticker = ticker.upper()
        # session and proxy are now handled by the data source strategy if needed.

        self._strategy = DataSourceFactory.get_source()

        # Properties that are not yet migrated to the new architecture
        # can be initialized here if needed.
        self._news = []

    @utils.log_indent_decorator
    def history(self, *args, **kwargs):
        # proxy is handled by the underlying data fetcher if applicable
        return self._strategy.get_history(self.ticker, *args, **kwargs)

    def get_recommendations(self, proxy=_SENTINEL_, as_dict=False):
        return self._strategy.get_recommendations(self, proxy, as_dict=as_dict)

    def get_recommendations_summary(self, proxy=_SENTINEL_, as_dict=False):
        return self._strategy.get_recommendations_summary(self, proxy, as_dict=as_dict)

    def get_upgrades_downgrades(self, proxy=_SENTINEL_, as_dict=False):
        return self._strategy.get_upgrades_downgrades(self, proxy, as_dict=as_dict)

    def get_calendar(self, proxy=_SENTINEL_) -> dict:
        return self._strategy.get_calendar(self, proxy)

    def get_sec_filings(self, proxy=_SENTINEL_) -> dict:
        return self._strategy.get_sec_filings(self, proxy)

    def get_major_holders(self, proxy=_SENTINEL_, as_dict=False):
        return self._strategy.get_major_holders(self, proxy, as_dict=as_dict)

    def get_institutional_holders(self, proxy=_SENTINEL_, as_dict=False):
        return self._strategy.get_institutional_holders(self, proxy, as_dict=as_dict)

    def get_mutualfund_holders(self, proxy=_SENTINEL_, as_dict=False):
        return self._strategy.get_mutualfund_holders(self, proxy, as_dict=as_dict)

    def get_insider_purchases(self, proxy=_SENTINEL_, as_dict=False):
        return self._strategy.get_insider_purchases(self, proxy, as_dict=as_dict)

    def get_insider_transactions(self, proxy=_SENTINEL_, as_dict=False):
        return self._strategy.get_insider_transactions(self, proxy, as_dict=as_dict)

    def get_insider_roster_holders(self, proxy=_SENTINEL_, as_dict=False):
        return self._strategy.get_insider_roster_holders(self, proxy, as_dict=as_dict)

    def get_info(self, proxy=_SENTINEL_) -> dict:
        return self._strategy.get_info(self, proxy)

    def get_fast_info(self, proxy=_SENTINEL_):
        return self._strategy.get_fast_info(self, proxy)

    def get_sustainability(self, proxy=_SENTINEL_, as_dict=False):
        return self._strategy.get_sustainability(self, proxy, as_dict=as_dict)

    def get_analyst_price_targets(self, proxy=_SENTINEL_) -> dict:
        return self._strategy.get_analyst_price_targets(self, proxy)

    def get_earnings_estimate(self, proxy=_SENTINEL_, as_dict=False):
        return self._strategy.get_earnings_estimate(self, proxy, as_dict=as_dict)

    def get_revenue_estimate(self, proxy=_SENTINEL_, as_dict=False):
        return self._strategy.get_revenue_estimate(self, proxy, as_dict=as_dict)

    def get_earnings_history(self, proxy=_SENTINEL_, as_dict=False):
        return self._strategy.get_earnings_history(self, proxy, as_dict=as_dict)

    def get_eps_trend(self, proxy=_SENTINEL_, as_dict=False):
        return self._strategy.get_eps_trend(self, proxy, as_dict=as_dict)

    def get_eps_revisions(self, proxy=_SENTINEL_, as_dict=False):
        return self._strategy.get_eps_revisions(self, proxy, as_dict=as_dict)

    def get_growth_estimates(self, proxy=_SENTINEL_, as_dict=False):
        return self._strategy.get_growth_estimates(self, proxy, as_dict=as_dict)

    def get_earnings(self, proxy=_SENTINEL_, as_dict=False, freq="yearly"):
        return self._strategy.get_earnings(self, proxy, as_dict=as_dict, freq=freq)

    def get_income_stmt(self, proxy=_SENTINEL_, as_dict=False, pretty=False, freq="yearly"):
        return self._strategy.get_income_stmt(self, proxy, as_dict=as_dict, pretty=pretty, freq=freq)

    def get_incomestmt(self, proxy=_SENTINEL_, as_dict=False, pretty=False, freq="yearly"):
        return self.get_income_stmt(proxy, as_dict, pretty, freq)

    def get_financials(self, proxy=_SENTINEL_, as_dict=False, pretty=False, freq="yearly"):
        return self.get_income_stmt(proxy, as_dict, pretty, freq)

    def get_balance_sheet(self, proxy=_SENTINEL_, as_dict=False, pretty=False, freq="yearly"):
        return self._strategy.get_balance_sheet(self, proxy, as_dict=as_dict, pretty=pretty, freq=freq)

    def get_balancesheet(self, proxy=_SENTINEL_, as_dict=False, pretty=False, freq="yearly"):
        return self.get_balance_sheet(proxy, as_dict, pretty, freq)

    def get_cash_flow(self, proxy=_SENTINEL_, as_dict=False, pretty=False, freq="yearly") -> Union[pd.DataFrame, dict]:
        return self._strategy.get_cash_flow(self, proxy, as_dict=as_dict, pretty=pretty, freq=freq)

    def get_cashflow(self, proxy=_SENTINEL_, as_dict=False, pretty=False, freq="yearly"):
        return self.get_cash_flow(proxy, as_dict, pretty, freq)

    def get_dividends(self, proxy=_SENTINEL_, period="max") -> pd.Series:
        return self._strategy.get_dividends(self, proxy, period=period)

    def get_capital_gains(self, proxy=_SENTINEL_, period="max") -> pd.Series:
        return self._strategy.get_capital_gains(self, proxy, period=period)

    def get_splits(self, proxy=_SENTINEL_, period="max") -> pd.Series:
        return self._strategy.get_splits(self, proxy, period=period)

    def get_actions(self, proxy=_SENTINEL_, period="max") -> pd.Series:
        return self._strategy.get_actions(self, proxy, period=period)

    def get_shares(self, proxy=_SENTINEL_, as_dict=False) -> Union[pd.DataFrame, dict]:
        return self._strategy.get_shares(self, proxy, as_dict=as_dict)

    @utils.log_indent_decorator
    def get_shares_full(self, start=None, end=None, proxy=_SENTINEL_):
        return self._strategy.get_shares_full(self, start, end, proxy=proxy)

    def get_isin(self, proxy=_SENTINEL_) -> Optional[str]:
        return self._strategy.get_isin(self, proxy)

    def get_news(self, count=10, tab="news", proxy=_SENTINEL_) -> list:
        return self._strategy.get_news(self, count, tab, proxy=proxy)

    @utils.log_indent_decorator
    def get_earnings_dates(self, limit=12, proxy=_SENTINEL_) -> Optional[pd.DataFrame]:
        return self._strategy.get_earnings_dates(self, limit, proxy=proxy)

    def get_history_metadata(self, proxy=_SENTINEL_) -> dict:
        return self._strategy.get_history_metadata(self, proxy=proxy)

    def get_funds_data(self, proxy=_SENTINEL_) -> Optional[FundsData]:
        return self._strategy.get_funds_data(self, proxy=proxy)

    def live(self, message_handler=None, verbose=True):
        self._strategy.live(self, message_handler=message_handler, verbose=verbose)