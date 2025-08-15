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

# 从本地模块导入版本信息
from . import version
# 从本地模块导入搜索功能
from .search import Search
# 从本地模块导入查找功能
from .lookup import Lookup
# 从本地模块导入Ticker类，用于处理单个股票代码
from .ticker import Ticker
# 从本地模块导入Tickers类，用于处理多个股票代码
from .tickers import Tickers
# 从本地模块导入download函数，用于下载数据
from .multi import download
# 从本地模块导入WebSocket和AsyncWebSocket，用于实时数据流
from .live import WebSocket, AsyncWebSocket
# 从本地模块导入工具函数
from .utils import enable_debug_mode
# 从本地模块导入缓存相关的函数
from .cache import set_tz_cache_location
# 从本地模块导入领域相关的类
from .domain.sector import Sector
from .domain.industry import Industry
from .domain.market import Market
# 从本地模块导入YfData类
from .data import YfData

# 从screener子包导入查询和筛选功能
from .screener.query import EquityQuery, FundQuery
from .screener.screener import screen, PREDEFINED_SCREENER_QUERIES

# 设置版本号和作者信息
__version__ = version.version
__author__ = "Ran Aroussi"

# 导入warnings模块，用于处理警告信息
import warnings
# 设置警告过滤器，默认显示yfinance模块的DeprecationWarning
warnings.filterwarnings('default', category=DeprecationWarning, module='^yfinance')

# 定义__all__列表，指定通过 'from yfinance import *' 导入的模块
__all__ = ['download', 'Market', 'Search', 'Lookup', 'Ticker', 'Tickers', 'enable_debug_mode', 'set_tz_cache_location', 'Sector', 'Industry', 'WebSocket', 'AsyncWebSocket']
# 添加screener相关的模块到__all__
__all__ += ['EquityQuery', 'FundQuery', 'screen', 'PREDEFINED_SCREENER_QUERIES']

# 配置相关
_NOTSET=object()
def set_config(proxy=_NOTSET):
    """
    设置全局配置。
    目前只支持设置代理。
    """
    if proxy is not _NOTSET:
        YfData(proxy=proxy)
__all__ += ["set_config"]
