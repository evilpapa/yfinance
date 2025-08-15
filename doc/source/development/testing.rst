单元测试
----------

测试是使用Python的 `unittest` 模块编写的。以下是一些运行测试的方法：

- **运行所有价格测试**:

  .. code-block:: bash

     python -m unittest tests.test_prices

- **运行价格测试的子集**:

  .. code-block:: bash

     python -m unittest tests.test_prices.TestPriceRepair

- **运行特定测试**:

  .. code-block:: bash

     python -m unittest tests.test_prices_repair.TestPriceRepair.test_ticker_missing

- **通用命令**:

  ..code-block:: bash

     python -m unittest tests.{file}.{class}.{method}

- **运行所有测试**:

  .. code-block:: bash

     python -m unittest discover -s tests

.. note::

    测试目前已经失败

    标准结果:

    **失败:** 11

    **错误:** 93

    **跳过:** 1

.. seealso::

    有关更多信息，请参阅 ` ``unittest`` 模块 <https://docs.python.org/3/library/unittest.html>`_。
