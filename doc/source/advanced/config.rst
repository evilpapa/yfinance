******
配置
******

`yfinance` 有一个新的全局配置，用于共享通用值。

代理
-----

在配置中设置一次代理，会影响所有 yfinance 数据获取。

.. code-block:: python

   import yfinance as yf
   yf.set_config(proxy="PROXY_SERVER")
