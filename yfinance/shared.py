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

# _DFS: 存储下载的DataFrame的字典
_DFS = {}
# _PROGRESS_BAR: 进度条对象
_PROGRESS_BAR = None
# _ERRORS: 存储下载错误的字典
_ERRORS = {}
# _TRACEBACKS: 存储错误的追溯信息的字典
_TRACEBACKS = {}
# _ISINS: 存储ISIN码与股票代码的映射
_ISINS = {}
