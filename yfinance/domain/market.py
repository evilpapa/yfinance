import datetime as dt
import json as _json
import warnings

from ..const import _QUERY1_URL_, _SENTINEL_
from ..data import utils, YfData

class Market:
    """
    表示一个金融市场，用于获取该市场的摘要和状态信息。
    """
    def __init__(self, market:'str', session=None, proxy=_SENTINEL_, timeout=30):
        """
        初始化Market对象。

        参数:
            market (str): 市场名称，例如 "us_market"。
            session (optional): 用于请求的会话。
            proxy (optional): 代理服务器。
            timeout (int): 请求超时时间。
        """
        self.market = market
        self.session = session
        self.timeout = timeout

        self._data = YfData(session=self.session)
        if proxy is not _SENTINEL_:
            warnings.warn("Set proxy via new config function: yf.set_config(proxy=proxy)", DeprecationWarning, stacklevel=2)
            self._data._set_proxy(proxy)

        self._logger = utils.get_yf_logger()
        
        self._status = None
        self._summary = None

    def _fetch_json(self, url, params):
        """获取并解析JSON数据"""
        data = self._data.cache_get(url=url, params=params, timeout=self.timeout)
        if data is None or "Will be right back" in data.text:
            raise RuntimeError("*** YAHOO! FINANCE IS CURRENTLY DOWN! ***\n"
                               "Our engineers are working quickly to resolve "
                               "the issue. Thank you for your patience.")
        try:
            return data.json()
        except _json.JSONDecodeError:
            self._logger.error(f"{self.market}: Failed to retrieve market data and recieved faulty data.")
            return {}
        
    def _parse_data(self):
        """解析市场数据"""
        # 获取两者以确保它们在同一时间
        if (self._status is not None) and (self._summary is not None):
            return
        
        self._logger.debug(f"{self.market}: Parsing market data")

        # 摘要
        summary_url = f"{_QUERY1_URL_}/v6/finance/quote/marketSummary"
        summary_fields = ["shortName", "regularMarketPrice", "regularMarketChange", "regularMarketChangePercent"]
        summary_params = {
            "fields": ",".join(summary_fields),
            "formatted": False,
            "lang": "en-US",
            "market": self.market
        }

        # 状态
        status_url = f"{_QUERY1_URL_}/v6/finance/markettime"
        status_params = {
            "formatted": True,
            "key": "finance",
            "lang": "en-US",
            "market": self.market
        }

        self._summary = self._fetch_json(summary_url, summary_params)
        self._status = self._fetch_json(status_url, status_params)

        try:
            self._summary = self._summary['marketSummaryResponse']['result']
            self._summary = {x['exchange']:x for x in self._summary}
        except Exception as e:
            self._logger.error(f"{self.market}: Failed to parse market summary")
            self._logger.debug(f"{type(e)}: {e}")


        try:
            # 解包
            self._status = self._status['finance']['marketTimes'][0]['marketTime'][0]
            self._status['timezone'] = self._status['timezone'][0]
            del self._status['time']  # 多余
            try:
                self._status.update({
                    "open": dt.datetime.fromisoformat(self._status["open"]),
                    "close": dt.datetime.fromisoformat(self._status["close"]),
                    "tz": dt.timezone(dt.timedelta(hours=int(self._status["timezone"]["gmtoffset"]))/1000, self._status["timezone"]["short"])
                })
            except Exception as e:
                self._logger.error(f"{self.market}: Failed to update market status")
                self._logger.debug(f"{type(e)}: {e}")
        except Exception as e:
            self._logger.error(f"{self.market}: Failed to parse market status")
            self._logger.debug(f"{type(e)}: {e}")

    @property
    def status(self):
        """获取市场状态"""
        self._parse_data()
        return self._status

    @property
    def summary(self):
        """获取市场摘要"""
        self._parse_data()
        return self._summary
