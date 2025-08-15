缓存
=======

持久缓存
----------------

为了减少对雅虎的请求，yfinance会在本地存储一些数据：用于本地化日期的时区和cookie。缓存位置如下：

- Windows = C:/Users/<USER>/AppData/Local/py-yfinance
- Linux = /home/<USER>/.cache/py-yfinance
- MacOS = /Users/<USER>/Library/Caches/py-yfinance

您可以使用 :attr:`set_tz_cache_location <yfinance.set_tz_cache_location>` 来指定缓存使用不同的位置：

.. code-block:: python

    import yfinance as yf
    yf.set_tz_cache_location("custom/cache/location")