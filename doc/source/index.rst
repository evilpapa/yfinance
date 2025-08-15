yfinance 文档
======================

从雅虎财经API下载市场数据
----------------------------------------------

.. admonition:: 重要法律免责声明

   **Yahoo!、Y!Finance 和 Yahoo! finance 是雅虎公司的注册商标。**

   yfinance 与雅虎公司**没有**关联，也未得到其认可或审查。它是一个
   开源工具，使用雅虎的公开可用API，旨在
   用于研究和教育目的。

   **您应参考雅虎的使用条款**
   (`此处 <https://policies.yahoo.com/us/en/yahoo/terms/product-atos/apiforydn/index.htm>`__),
   (`此处 <https://legal.yahoo.com/us/en/yahoo/terms/otos/index.html>`__),
   和 (`此处 <https://policies.yahoo.com/us/en/yahoo/terms/index.htm>`__)
   以了解您使用下载数据的权利详情。
   请记住 - 雅虎财经API仅供个人使用。

安装
-------

.. code-block:: bash

    $ pip install yfinance

快速入门
-----------

展示 yfinance API 的一小部分示例，完整的 API 要大得多，并在 :doc:`reference/index` 中介绍。

.. code-block:: python

   import yfinance as yf
   dat = yf.Ticker("MSFT")


单个股票代码

.. code-block:: python

   dat = yf.Ticker("MSFT")
   dat.info
   dat.calendar
   dat.analyst_price_targets
   dat.quarterly_income_stmt
   dat.history(period='1mo')
   dat.option_chain(dat.options[0]).calls

多个股票代码

.. code-block:: python

   tickers = yf.Tickers('MSFT AAPL GOOG')
   tickers.tickers['MSFT'].info
   yf.download(['MSFT', 'AAPL', 'GOOG'], period='1mo')

基金

.. code-block:: python

   spy = yf.Ticker('SPY').funds_data
   spy.description
   spy.top_holdings

.. toctree::
   :maxdepth: 1
   :titlesonly:
   :caption: 目录

   advanced/index
   reference/index
   development/index
