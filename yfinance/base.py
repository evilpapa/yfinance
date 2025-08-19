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

import json as _json
import warnings
from typing import Optional, Union
from urllib.parse import quote as urlencode

import numpy as np
import pandas as pd
from curl_cffi import requests


from . import utils, cache
from .data import YfData
from .exceptions import YFEarningsDateMissing, YFRateLimitError
from .live import WebSocket
from .datasources.factory import DataSourceFactory
from .exceptions import YFEarningsDateMissing, YFRateLimitError
from .live import WebSocket
from .const import _SENTINEL_
from . import utils

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

    def get_info(self, proxy=_SENTINEL_):
        # proxy is handled by the underlying data fetcher if applicable
        return self._strategy.get_info(self.ticker, proxy=proxy)

    def get_income_stmt(self, proxy=_SENTINEL_, as_dict=False, pretty=False, freq="yearly"):
        return self._strategy.get_income_stmt(self.ticker, proxy=proxy, as_dict=as_dict, pretty=pretty, freq=freq)

    def get_balance_sheet(self, proxy=_SENTINEL_, as_dict=False, pretty=False, freq="yearly"):
        return self._strategy.get_balance_sheet(self.ticker, proxy=proxy, as_dict=as_dict, pretty=pretty, freq=freq)

    def get_cash_flow(self, proxy=_SENTINEL_, as_dict=False, pretty=False, freq="yearly"):
        return self._strategy.get_cash_flow(self.ticker, proxy=proxy, as_dict=as_dict, pretty=pretty, freq=freq)

    # Aliases for financials, as per original yfinance
    def get_incomestmt(self, *args, **kwargs):
        return self.get_income_stmt(*args, **kwargs)

    def get_financials(self, *args, **kwargs):
        return self.get_income_stmt(*args, **kwargs)

    def get_balancesheet(self, *args, **kwargs):
        return self.get_balance_sheet(*args, **kwargs)

    def get_cashflow(self, *args, **kwargs):
        return self.get_cash_flow(*args, **kwargs)

    # Methods that have not been migrated to the new architecture yet.
    # They will raise NotImplementedError.
    def get_recommendations(self, *args, **kwargs):
        raise NotImplementedError("get_recommendations has not been migrated to the new architecture.")

    def get_recommendations_summary(self, *args, **kwargs):
        raise NotImplementedError("get_recommendations_summary has not been migrated to the new architecture.")

    def get_upgrades_downgrades(self, *args, **kwargs):
        raise NotImplementedError("get_upgrades_downgrades has not been migrated to the new architecture.")

    def get_calendar(self, *args, **kwargs):
        raise NotImplementedError("get_calendar has not been migrated to the new architecture.")

    def get_sec_filings(self, *args, **kwargs):
        raise NotImplementedError("get_sec_filings has not been migrated to the new architecture.")

    def get_major_holders(self, *args, **kwargs):
        raise NotImplementedError("get_major_holders has not been migrated to the new architecture.")

    def get_institutional_holders(self, *args, **kwargs):
        raise NotImplementedError("get_institutional_holders has not been migrated to the new architecture.")

    def get_mutualfund_holders(self, *args, **kwargs):
        raise NotImplementedError("get_mutualfund_holders has not been migrated to the new architecture.")

    def get_insider_purchases(self, *args, **kwargs):
        raise NotImplementedError("get_insider_purchases has not been migrated to the new architecture.")

    def get_insider_transactions(self, *args, **kwargs):
        raise NotImplementedError("get_insider_transactions has not been migrated to the new architecture.")

    def get_insider_roster_holders(self, *args, **kwargs):
        raise NotImplementedError("get_insider_roster_holders has not been migrated to the new architecture.")

    def get_sustainability(self, *args, **kwargs):
        raise NotImplementedError("get_sustainability has not been migrated to the new architecture.")
        
    def get_analyst_price_targets(self, *args, **kwargs):
        raise NotImplementedError("get_analyst_price_targets has not been migrated to the new architecture.")

    def get_earnings_estimate(self, *args, **kwargs):
        raise NotImplementedError("get_earnings_estimate has not been migrated to the new architecture.")

    def get_revenue_estimate(self, *args, **kwargs):
        raise NotImplementedError("get_revenue_estimate has not been migrated to the new architecture.")

    def get_earnings_history(self, *args, **kwargs):
        raise NotImplementedError("get_earnings_history has not been migrated to the new architecture.")

    def get_eps_trend(self, *args, **kwargs):
        raise NotImplementedError("get_eps_trend has not been migrated to the new architecture.")

    def get_eps_revisions(self, *args, **kwargs):
        raise NotImplementedError("get_eps_revisions has not been migrated to the new architecture.")

    def get_growth_estimates(self, *args, **kwargs):
        raise NotImplementedError("get_growth_estimates has not been migrated to the new architecture.")

    def get_earnings(self, *args, **kwargs):
        raise NotImplementedError("get_earnings has not been migrated to the new architecture.")

    def get_dividends(self, *args, **kwargs):
        raise NotImplementedError("get_dividends has not been migrated to the new architecture.")

    def get_capital_gains(self, *args, **kwargs):
        raise NotImplementedError("get_capital_gains has not been migrated to the new architecture.")

    def get_splits(self, *args, **kwargs):
        raise NotImplementedError("get_splits has not been migrated to the new architecture.")

    def get_actions(self, *args, **kwargs):
        raise NotImplementedError("get_actions has not been migrated to the new architecture.")

    def get_shares(self, *args, **kwargs):
        raise NotImplementedError("get_shares has not been migrated to the new architecture.")

    def get_isin(self, *args, **kwargs):
        raise NotImplementedError("get_isin has not been migrated to the new architecture.")

    def get_news(self, *args, **kwargs):
        return self._news

    def get_earnings_dates(self, *args, **kwargs):
        raise NotImplementedError("get_earnings_dates has not been migrated to the new architecture.")

    def get_history_metadata(self, *args, **kwargs):
        raise NotImplementedError("get_history_metadata has not been migrated to the new architecture.")

    def get_funds_data(self, *args, **kwargs):
        raise NotImplementedError("get_funds_data has not been migrated to the new architecture.")

    def live(self, *args, **kwargs):
        raise NotImplementedError("live has not been migrated to the new architecture.")
