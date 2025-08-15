=============
API 参考
=============

概述
--------

`yfinance` 包可以轻松访问Yahoo! Finance的API以检索市场数据。它包括用于下载历史市场数据、访问股票代码信息、管理缓存等的类和函数。


公共API
==========

以下是`yfinance`包公开的类和函数：

- :attr:`Ticker <yfinance.Ticker>`: 用于访问单个股票代码数据的类。
- :attr:`Tickers <yfinance.Tickers>`: 用于处理多个股票代码的类。
- :attr:`Market <yfinance.Market>`: 用于访问市场摘要的类。
- :attr:`download <yfinance.download>`: 用于下载多个股票代码的市场数据的函数。
- :attr:`Search <yfinance.Search>`: 用于访问搜索结果的类。
- :attr:`Lookup <yfinance.Lookup>`: 用于查找股票代码的类。
- :class:`WebSocket <yfinance.WebSocket>`: 用于同步流式传输实时市场数据的类。
- :class:`AsyncWebSocket <yfinance.AsyncWebSocket>`: 用于异步流式传输实时市场数据的类。
- :attr:`Sector <yfinance.Sector>`: 用于访问行业信息的域类。
- :attr:`Industry <yfinance.Industry>`: 用于访问行业信息的域类。
- :attr:`Market <yfinance.Market>`: 用于访问市场状态和摘要的类。
- :attr:`EquityQuery <yfinance.EquityQuery>`: 用于构建股票查询过滤器的类。
- :attr:`FundQuery <yfinance.FundQuery>`: 用于构建基金查询过滤器的类。
- :attr:`screen <yfinance.screen>`: 运行股票/基金查询。
- :attr:`enable_debug_mode <yfinance.enable_debug_mode>`: 用于启用日志记录调试模式的函数。
- :attr:`set_tz_cache_location <yfinance.set_tz_cache_location>`: 用于设置时区缓存位置的函数。

.. toctree::
   :maxdepth: 1
   :hidden:


   yfinance.ticker_tickers
   yfinance.stock
   yfinance.market
   yfinance.financials
   yfinance.analysis
   yfinance.market
   yfinance.search
   yfinance.lookup
   yfinance.websocket
   yfinance.sector_industry
   yfinance.screener
   yfinance.functions

   yfinance.funds_data
   yfinance.price_history
