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
import warnings

from . import utils
from .const import _BASE_URL_, _SENTINEL_
from .data import YfData


class Search:
    """
    从Yahoo Finance获取和组织搜索结果，包括股票报价和新闻文章。

    参数:
        query: 搜索查询（股票代码或公司名称）。
        max_results: 返回的最大股票报价数（默认为8）。
        news_count: 要包含的新闻文章数（默认为8）。
        lists_count: 要包含的列表数（默认为8）。
        include_cb: 包括公司明细（默认为True）。
        include_nav_links: 包括导航链接（默认为False）。
        include_research: 包括研究报告（默认为False）。
        include_cultural_assets: 包括文化资产（默认为False）。
        enable_fuzzy_query: 启用模糊搜索以处理拼写错误（默认为False）。
        recommended: 建议返回的结果数（默认为8）。
        session: 用于请求的自定义HTTP会话（默认为None）。
        timeout: 请求超时（秒）（默认为30）。
        raise_errors: 出错时引发异常（默认为True）。
    """

    def __init__(self, query, max_results=8, news_count=8, lists_count=8, include_cb=True, include_nav_links=False,
                 include_research=False, include_cultural_assets=False, enable_fuzzy_query=False, recommended=8,
                 session=None, proxy=_SENTINEL_, timeout=30, raise_errors=True):
        self.session = session
        self._data = YfData(session=self.session)
        
        if proxy is not _SENTINEL_:
            warnings.warn("Set proxy via new config function: yf.set_config(proxy=proxy)", DeprecationWarning, stacklevel=2)
            self._data._set_proxy(proxy)

        self.query = query
        self.max_results = max_results
        self.enable_fuzzy_query = enable_fuzzy_query
        self.news_count = news_count
        self.timeout = timeout
        self.raise_errors = raise_errors

        self.lists_count = lists_count
        self.include_cb = include_cb
        self.nav_links = include_nav_links
        self.enable_research = include_research
        self.enable_cultural_assets = include_cultural_assets
        self.recommended = recommended

        self._logger = utils.get_yf_logger()

        self._response = {}
        self._all = {}
        self._quotes = []
        self._news = []
        self._lists = []
        self._research = []
        self._nav = []

        self.search()

    def search(self) -> 'Search':
        """使用构造函数中定义的查询参数进行搜索。"""
        url = f"{_BASE_URL_}/v1/finance/search"
        params = {
            "q": self.query,
            "quotesCount": self.max_results,
            "enableFuzzyQuery": self.enable_fuzzy_query,
            "newsCount": self.news_count,
            "quotesQueryId": "tss_match_phrase_query",
            "newsQueryId": "news_cie_vespa",
            "listsCount": self.lists_count,
            "enableCb": self.include_cb,
            "enableNavLinks": self.nav_links,
            "enableResearchReports": self.enable_research,
            "enableCulturalAssets": self.enable_cultural_assets,
            "recommendedCount": self.recommended
        }

        self._logger.debug(f'{self.query}: Yahoo GET parameters: {str(dict(params))}')

        data = self._data.cache_get(url=url, params=params, timeout=self.timeout)
        if data is None or "Will be right back" in data.text:
            raise RuntimeError("*** YAHOO! FINANCE IS CURRENTLY DOWN! ***\n"
                               "Our engineers are working quickly to resolve "
                               "the issue. Thank you for your patience.")
        try:
            data = data.json()
        except _json.JSONDecodeError:
            self._logger.error(f"{self.query}: Failed to retrieve search results and received faulty response instead.")
            data = {}

        self._response = data
        self._quotes = [quote for quote in data.get("quotes", []) if "symbol" in quote]
        self._news = data.get("news", [])
        self._lists = data.get("lists", [])
        self._research = data.get("researchReports", [])
        self._nav = data.get("nav", [])

        self._all = {"quotes": self._quotes, "news": self._news, "lists": self._lists, "research": self._research,
                     "nav": self._nav}

        return self

    @property
    def quotes(self) -> 'list':
        """从搜索结果中获取报价。"""
        return self._quotes

    @property
    def news(self) -> 'list':
        """从搜索结果中获取新闻。"""
        return self._news

    @property
    def lists(self) -> 'list':
        """从搜索结果中获取列表。"""
        return self._lists

    @property
    def research(self) -> 'list':
        """从搜索结果中获取研究报告。"""
        return self._research

    @property
    def nav(self) -> 'list':
        """从搜索结果中获取导航链接。"""
        return self._nav

    @property
    def all(self) -> 'dict[str,list]':
        """从搜索结果中获取所有结果：响应的筛选版本。"""
        return self._all

    @property
    def response(self) -> 'dict':
        """从搜索结果中获取原始响应。"""
        return self._response
