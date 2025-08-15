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

import logging
import time as _time
import traceback
from typing import Union
import warnings

import multitasking as _multitasking
import pandas as _pd
from curl_cffi import requests

from . import Ticker, utils
from .data import YfData
from . import shared
from .const import _SENTINEL_

@utils.log_indent_decorator
def download(tickers, start=None, end=None, actions=False, threads=True,
             ignore_tz=None, group_by='column', auto_adjust=None, back_adjust=False,
             repair=False, keepna=False, progress=True, period=None, interval="1d",
             prepost=False, proxy=_SENTINEL_, rounding=False, timeout=10, session=None,
             multi_level_index=True) -> Union[_pd.DataFrame, None]:
    """
    下载雅虎股票数据
    :参数:
        tickers : str, list
            要下载的股票代码列表
        period : str
            有效期间: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max
            默认: 1mo
            使用period参数或使用start和end
        interval : str
            有效间隔: 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo
            日内数据不能超过最近60天
        start: str
            下载开始日期字符串 (YYYY-MM-DD) 或 _datetime, 包含。
            默认为99年前
            例如 for start="2020-01-01", 第一个数据点将在 "2020-01-01"
        end: str
            下载结束日期字符串 (YYYY-MM-DD) 或 _datetime, 不包含。
            默认为现在
            例如 for end="2023-01-01", 最后一个数据点将在 "2022-12-31"
        group_by : str
            按 'ticker' 或 'column' (默认) 分组
        prepost : bool
            在结果中包含盘前和盘后数据？
            默认为 False
        auto_adjust: bool
            自动调整所有OHLC？默认为 True
        repair: bool
            检测货币单位100倍混淆并尝试修复
            默认为 False
        keepna: bool
            保留Yahoo返回的NaN行？
            默认为 False
        actions: bool
            下载股息+股票拆分数据。默认为 False
        threads: bool / int
            用于批量下载的线程数。默认为 True
        ignore_tz: bool
            当从不同时区合并时，忽略datetime的那部分。
            默认取决于间隔。日内 = False。天+ = True。
        rounding: bool
            可选。将值四舍五入到2位小数？
        timeout: None or float
            如果不是None，则在给定秒数后停止等待响应。 (也可以是小数，例如 0.01)
        session: None or Session
            可选。传递您自己的会话对象以用于所有请求
        multi_level_index: bool
            可选。总是返回一个多级索引的DataFrame？默认为 True
    """
    logger = utils.get_yf_logger()
    session = session or requests.Session(impersonate="chrome")

    if proxy is not _SENTINEL_:
        warnings.warn("Set proxy via new config function: yf.set_config(proxy=proxy)", DeprecationWarning, stacklevel=3)
        YfData(proxy=proxy)
    YfData(session=session)

    if auto_adjust is None:
        warnings.warn("YF.download() has changed argument auto_adjust default to True", FutureWarning, stacklevel=3)
        auto_adjust = True

    if logger.isEnabledFor(logging.DEBUG):
        if threads:
            logger.debug('Disabling multithreading because DEBUG logging enabled')
            threads = False
        if progress:
            progress = False

    if ignore_tz is None:
        if interval[-1] in ['m', 'h']:
            ignore_tz = False
        else:
            ignore_tz = True

    tickers = tickers if isinstance(
        tickers, (list, set, tuple)) else tickers.replace(',', ' ').split()

    shared._ISINS = {}
    _tickers_ = []
    for ticker in tickers:
        if utils.is_isin(ticker):
            isin = ticker
            ticker = utils.get_ticker_by_isin(ticker)
            shared._ISINS[ticker] = isin
        _tickers_.append(ticker)

    tickers = _tickers_

    tickers = list(set([ticker.upper() for ticker in tickers]))

    if progress:
        shared._PROGRESS_BAR = utils.ProgressBar(len(tickers), 'completed')

    shared._DFS = {}
    shared._ERRORS = {}
    shared._TRACEBACKS = {}

    if threads:
        if threads is True:
            threads = min([len(tickers), _multitasking.cpu_count() * 2])
        _multitasking.set_max_threads(threads)
        for i, ticker in enumerate(tickers):
            _download_one_threaded(ticker, period=period, interval=interval,
                                   start=start, end=end, prepost=prepost,
                                   actions=actions, auto_adjust=auto_adjust,
                                   back_adjust=back_adjust, repair=repair, keepna=keepna,
                                   progress=(progress and i > 0),
                                   rounding=rounding, timeout=timeout)
        while len(shared._DFS) < len(tickers):
            _time.sleep(0.01)
    else:
        for i, ticker in enumerate(tickers):
            data = _download_one(ticker, period=period, interval=interval,
                                 start=start, end=end, prepost=prepost,
                                 actions=actions, auto_adjust=auto_adjust,
                                 back_adjust=back_adjust, repair=repair, keepna=keepna,
                                 rounding=rounding, timeout=timeout)
            if progress:
                shared._PROGRESS_BAR.animate()

    if progress:
        shared._PROGRESS_BAR.completed()

    if shared._ERRORS:
        logger = utils.get_yf_logger()
        logger.error('\n%.f Failed download%s:' % (
            len(shared._ERRORS), 's' if len(shared._ERRORS) > 1 else ''))

        errors = {}
        for ticker in shared._ERRORS:
            err = shared._ERRORS[ticker]
            err = err.replace(f'${ticker}: ', '')
            if err not in errors:
                errors[err] = [ticker]
            else:
                errors[err].append(ticker)
        for err in errors.keys():
            logger.error(f'{errors[err]}: ' + err)

        tbs = {}
        for ticker in shared._TRACEBACKS:
            tb = shared._TRACEBACKS[ticker]
            tb = tb.replace(f'${ticker}: ', '')
            if tb not in tbs:
                tbs[tb] = [ticker]
            else:
                tbs[tb].append(ticker)
        for tb in tbs.keys():
            logger.debug(f'{tbs[tb]}: ' + tb)

    if ignore_tz:
        for tkr in shared._DFS.keys():
            if (shared._DFS[tkr] is not None) and (shared._DFS[tkr].shape[0] > 0):
                shared._DFS[tkr].index = shared._DFS[tkr].index.tz_localize(None)

    try:
        data = _pd.concat(shared._DFS.values(), axis=1, sort=True,
                          keys=shared._DFS.keys(), names=['Ticker', 'Price'])
    except Exception:
        _realign_dfs()
        data = _pd.concat(shared._DFS.values(), axis=1, sort=True,
                          keys=shared._DFS.keys(), names=['Ticker', 'Price'])
    data.index = _pd.to_datetime(data.index, utc=not ignore_tz)
    data.rename(columns=shared._ISINS, inplace=True)

    if group_by == 'column':
        data.columns = data.columns.swaplevel(0, 1)
        data.sort_index(level=0, axis=1, inplace=True)

    if not multi_level_index and len(tickers) == 1:
        data = data.droplevel(0 if group_by == 'ticker' else 1, axis=1).rename_axis(None, axis=1)

    return data


def _realign_dfs():
    """重新对齐DataFrame"""
    idx_len = 0
    idx = None

    for df in shared._DFS.values():
        if len(df) > idx_len:
            idx_len = len(df)
            idx = df.index

    for key in shared._DFS.keys():
        try:
            shared._DFS[key] = _pd.DataFrame(
                index=idx, data=shared._DFS[key]).drop_duplicates()
        except Exception:
            shared._DFS[key] = _pd.concat([
                utils.empty_df(idx), shared._DFS[key].dropna()
            ], axis=0, sort=True)

        shared._DFS[key] = shared._DFS[key].loc[
            ~shared._DFS[key].index.duplicated(keep='last')]


@_multitasking.task
def _download_one_threaded(ticker, start=None, end=None,
                           auto_adjust=False, back_adjust=False, repair=False,
                           actions=False, progress=True, period="max",
                           interval="1d", prepost=False,
                           keepna=False, rounding=False, timeout=10):
    """使用线程下载单个股票数据"""
    _download_one(ticker, start, end, auto_adjust, back_adjust, repair,
                         actions, period, interval, prepost, rounding,
                         keepna, timeout)
    if progress:
        shared._PROGRESS_BAR.animate()


def _download_one(ticker, start=None, end=None,
                  auto_adjust=False, back_adjust=False, repair=False,
                  actions=False, period="max", interval="1d",
                  prepost=False, rounding=False,
                  keepna=False, timeout=10):
    """下载单个股票数据"""
    data = None
    try:
        data = Ticker(ticker).history(
                period=period, interval=interval,
                start=start, end=end, prepost=prepost,
                actions=actions, auto_adjust=auto_adjust,
                back_adjust=back_adjust, repair=repair,
                rounding=rounding, keepna=keepna, timeout=timeout,
                raise_errors=True
        )
    except Exception as e:
        shared._DFS[ticker.upper()] = utils.empty_df()
        shared._ERRORS[ticker.upper()] = repr(e)
        shared._TRACEBACKS[ticker.upper()] = traceback.format_exc()
    else:
        shared._DFS[ticker.upper()] = data

    return data
