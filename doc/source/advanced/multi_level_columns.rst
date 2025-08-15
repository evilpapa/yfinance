************************
多级列索引
************************

Stack Overflow上的以下答案是针对`如何处理yfinance下载的多级列名？<https://stackoverflow.com/questions/63107801>`_

- `yfinance`返回一个带有`pandas.DataFrame`的多级列名，其中一个级别是股票代码，另一个级别是股价数据

该答案讨论了：

- 如何在使用`pandas.DataFrame.to_csv`将数据帧保存为csv后正确读取多级列
- 如何将单个或多个股票代码下载到具有单级列名和股票代码列的单个数据帧中
