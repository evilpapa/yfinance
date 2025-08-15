日志记录
=======

`yfinance` 使用 `logging` 模块来处理消息。默认情况下，只记录错误。

如果需要调试，您可以使用以下代码切换到具有自定义格式的调试模式：

.. code-block:: python

   import yfinance as yf
   yf.enable_debug_mode()
