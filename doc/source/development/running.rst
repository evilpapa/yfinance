运行一个分支
================

使用PIP
--------

.. code-block:: bash

   pip install git+https://github.com/{user}/{repo}.git@{branch}

例如:

.. code-block:: bash

   pip install git+https://github.com/ranaroussi/yfinance.git@feature/name

使用Git
--------

1: 从GitHub下载:

.. code-block:: bash
    git clone https://github.com/{user}/{repo}.git
    pip install -r ./yfinance/requirements.txt

或者如果是一个特定的分支:

.. code-block:: bash
    git clone -b {branch} https://github.com/{user}/{repo}.git
    pip install -r ./yfinance/requirements.txt

.. NOTE::
    只有在全局安装时才执行下一步

    如果您是为1个特定项目安装，则可以跳过此步骤
    只需在项目目录中`git clone`

2. 将下载位置添加到Python搜索路径

两种不同的方法，选择一种：

1) 将路径添加到 ``PYTHONPATH`` 环境变量

2) 添加到Python文件的顶部:
.. code-block:: python
    import sys
    sys.path.insert(0, "path/to/downloaded/yfinance")


3: 验证

.. code-block:: python
    import yfinance
    print(yfinance)

输出应该是:

`<module 'yfinance' from 'path/to/downloaded/yfinance/yfinance/__init__.py'>`

如果输出看起来像这样，那么您第2步做错了

`<module 'yfinance' from '.../lib/python3.10/site-packages/yfinance/__init__.py'>`
