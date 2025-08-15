<img src="./doc/yfinance-gh-logo-dark.webp#gh-dark-mode-only" height="100">
<img src="./doc/yfinance-gh-logo-light.webp#gh-light-mode-only" height="100">

# 从雅虎财经API下载市场数据

<a target="new" href="https://pypi.python.org/pypi/yfinance"><img border=0 src="https://img.shields.io/badge/python-2.7,%203.6+-blue.svg?style=flat" alt="Python version"></a>
<a target="new" href="https://pypi.python.org/pypi/yfinance"><img border=0 src="https://img.shields.io/pypi/v/yfinance.svg?maxAge=60%" alt="PyPi version"></a>
<a target="new" href="https://pypi.python.org/pypi/yfinance"><img border=0 src="https://img.shields.io/pypi/status/yfinance.svg?maxAge=60" alt="PyPi status"></a>
<a target="new" href="https://pypi.python.org/pypi/yfinance"><img border=0 src="https://img.shields.io/pypi/dm/yfinance.svg?maxAge=2592000&label=installs&color=%2327B1FF" alt="PyPi downloads"></a>
<a target="new" href="https://github.com/ranaroussi/yfinance"><img border=0 src="https://img.shields.io/github/stars/ranaroussi/yfinance.svg?style=social&label=Star&maxAge=60" alt="Star this repo"></a>
<a target="new" href="https://x.com/intent/follow?screen_name=aroussi"><img border=0 src="https://img.shields.io/twitter/follow/aroussi.svg?style=social&label=Follow&maxAge=60" alt="Follow me on twitter"></a>



**yfinance** 提供了一种Python化的方式来从[雅虎财经](https://finance.yahoo.com)获取金融和市场数据。

---

> [!IMPORTANT]
> **Yahoo!、Y!Finance和Yahoo! finance是雅虎公司的注册商标。**
>
> yfinance与雅虎公司没有任何关联，也未获得其认可或审核。它是一个开源工具，使用雅虎的公开API，仅用于研究和教育目的。
>
> **您应参考雅虎的使用条款**（[此处](https://policies.yahoo.com/us/en/yahoo/terms/product-atos/apiforydn/index.htm)、[此处](https://legal.yahoo.com/us/en/yahoo/terms/otos/index.html)和[此处](https://policies.yahoo.com/us/en/yahoo/terms/index.htm)）**以了解您使用下载数据的权利详情。
>
> 请记住 - 雅虎财经API仅供个人使用。**

---

> [!TIP]
> 新的文档网站现已上线！🤘
>
> 访问 [**ranaroussi.github.io/yfinance**](https://ranaroussi.github.io/yfinance)

---

## 主要组件

- `Ticker`: 单个股票代码的数据
- `Tickers`: 多个股票代码的数据
- `download`: 下载多个股票代码的市场数据
- `Market`: 获取市场信息
- `WebSocket` 和 `AsyncWebSocket`: 实时流数据
- `Search`: 从搜索中获取报价和新闻
- `Sector` 和 `Industry`: 板块和行业信息
- `EquityQuery` 和 `Screener`: 构建查询以筛选市场

## 安装

使用`pip`从PYPI安装`yfinance`:

``` {.sourceCode .bash}
$ pip install yfinance
```

### [yfinance依靠社区来调查错误和贡献代码。这是您可以提供帮助的方式。](CONTRIBUTING.md)

---

![Star History Chart](https://api.star-history.com/svg?repos=ranaroussi/yfinance)

---

### 法律声明

**yfinance** 是根据 **Apache软件许可证** 分发的。有关详细信息，请参阅发布中的[LICENSE.txt](./LICENSE.txt)文件。

再次声明 - yfinance与雅虎公司没有任何关联，也未获得其认可或审核。它是一个开源工具，使用雅虎的公开API，仅用于研究和教育目的。您应参考雅虎的使用条款（[此处](https://policies.yahoo.com/us/en/yahoo/terms/product-atos/apiforydn/index.htm)、[此处](https://legal.yahoo.com/us/en/yahoo/terms/otos/index.html)和[此处](https://policies.yahoo.com/us/en/yahoo/terms/index.htm)）以了解您使用下载数据的权利详情。

---

### 附言

如果您有任何反馈，请给我留言。

**Ran Aroussi**
