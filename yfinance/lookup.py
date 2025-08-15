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

import json as _json
import pandas as pd
import warnings

from . import utils
from .const import _QUERY1_URL_, _SENTINEL_
from .data import YfData
from .exceptions import YFException

LOOKUP_TYPES = ["all", "equity", "mutualfund", "etf", "index", "future", "currency", "cryptocurrency"]


class Lookup:
    """
    从Yahoo Finance获取报价（股票代码）查找。

    :param query: 金融数据查找的搜索查询。
    :type query: str
    :param session: 用于请求的自定义HTTP会话（默认为None）。
    :param proxy: 请求的代理设置（默认为None）。
    :param timeout: 请求超时（秒）（默认为30）。
    :param raise_errors: 出错时引发异常（默认为True）。
    """

    def __init__(self, query: str, session=None, proxy=_SENTINEL_, timeout=30, raise_errors=True):
        self.session = session
        self._data = YfData(session=self.session)

        if proxy is not _SENTINEL_:
            warnings.warn("Set proxy via new config function: yf.set_config(proxy=proxy)", DeprecationWarning, stacklevel=2)
            self._data._set_proxy(proxy)

        self.query = query

        self.timeout = timeout
        self.raise_errors = raise_errors

        self._logger = utils.get_yf_logger()

        self._cache = {}

    def _fetch_lookup(self, lookup_type="all", count=25) -> dict:
        """获取查找结果"""
        cache_key = (lookup_type, count)
        if cache_key in self._cache:
            return self._cache[cache_key]

        url = f"{_QUERY1_URL_}/v1/finance/lookup"
        params = {
            "query": self.query,
            "type": lookup_type,
            "start": 0,
            "count": count,
            "formatted": False,
            "fetchPricingData": True,
            "lang": "en-US",
            "region": "US"
        }

        self._logger.debug(f'GET Lookup for ticker ({self.query}) with parameters: {str(dict(params))}')

        data = self._data.get(url=url, params=params, timeout=self.timeout)
        if data is None or "Will be right back" in data.text:
            raise RuntimeError("*** YAHOO! FINANCE IS CURRENTLY DOWN! ***\n"
                               "Our engineers are working quickly to resolve "
                               "the issue. Thank you for your patience.")
        try:
            data = data.json()
        except _json.JSONDecodeError:
            self._logger.error(f"{self.query}: Failed to retrieve lookup results and received faulty response instead.")
            data = {}

        # 返回错误
        if data.get("finance", {}).get("error", {}):
            raise YFException(data.get("finance", {}).get("error", {}))

        self._cache[cache_key] = data
        return data

    @staticmethod
    def _parse_response(response: dict) -> pd.DataFrame:
        """解析响应"""
        finance = response.get("finance", {})
        result = finance.get("result", [])
        result = result[0] if len(result) > 0 else {}
        documents = result.get("documents", [])
        df = pd.DataFrame(documents)
        if "symbol" not in df.columns:
            return pd.DataFrame()
        return df.set_index("symbol")

    def _get_data(self, lookup_type: str, count: int = 25) -> pd.DataFrame:
        """获取数据"""
        return self._parse_response(self._fetch_lookup(lookup_type, count))

    def get_all(self, count=25) -> pd.DataFrame:
        """
        返回所有可用的金融工具。

        :param count: 要检索的结果数。
        :type count: int
        """
        return self._get_data("all", count)

    def get_stock(self, count=25) -> pd.DataFrame:
        """
        返回与股票相关的金融工具。

        :param count: 要检索的结果数。
        :type count: int
        """
        return self._get_data("equity", count)

    def get_mutualfund(self, count=25) -> pd.DataFrame:
        """
        返回与共同基金相关的金融工具。

        :param count: 要检索的结果数。
        :type count: int
        """
        return self._get_data("mutualfund", count)

    def get_etf(self, count=25) -> pd.DataFrame:
        """
        返回与ETF相关的金融工具。

        :param count: 要检索的结果数。
        :type count: int
        """
        return self._get_data("etf", count)

    def get_index(self, count=25) -> pd.DataFrame:
        """
        返回与指数相关的金融工具。

        :param count: 要检索的结果数。
        :type count: int
        """
        return self._get_data("index", count)

    def get_future(self, count=25) -> pd.DataFrame:
        """
        返回与期货相关的金融工具。

        :param count: 要检索的结果数。
        :type count: int
        """
        return self._get_data("future", count)

    def get_currency(self, count=25) -> pd.DataFrame:
        """
        返回与货币相关的金融工具。

        :param count: 要检索的结果数。
        :type count: int
        """
        return self._get_data("currency", count)

    def get_cryptocurrency(self, count=25) -> pd.DataFrame:
        """
        返回与加密货币相关的金融工具。

        :param count: 要检索的结果数。
        :type count: int
        """
        return self._get_data("cryptocurrency", count)

    @property
    def all(self) -> pd.DataFrame:
        """返回所有可用的金融工具。"""
        return self._get_data("all")

    @property
    def stock(self) -> pd.DataFrame:
        """返回与股票相关的金融工具。"""
        return self._get_data("equity")

    @property
    def mutualfund(self) -> pd.DataFrame:
        """返回与共同基金相关的金融工具。"""
        return self._get_data("mutualfund")

    @property
    def etf(self) -> pd.DataFrame:
        """返回与ETF相关的金融工具。"""
        return self._get_data("etf")

    @property
    def index(self) -> pd.DataFrame:
        """返回与指数相关的金融工具。"""
        return self._get_data("index")

    @property
    def future(self) -> pd.DataFrame:
        """返回与期货相关的金融工具。"""
        return self._get_data("future")

    @property
    def currency(self) -> pd.DataFrame:
        """返回与货币相关的金融工具。"""
        return self._get_data("currency")

    @property
    def cryptocurrency(self) -> pd.DataFrame:
        """返回与加密货币相关的金融工具。"""
        return self._get_data("cryptocurrency")
