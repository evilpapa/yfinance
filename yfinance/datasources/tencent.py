import re
import pandas as pd
from typing import Dict, Any, Optional

from .generic import GenericDataSource

class TencentDataSource(GenericDataSource):
    """
    Data source for fetching data from Tencent Finance.
    Overrides get_info to handle the specific string-based format from Tencent.
    """

    def get_info(self, ticker: str, proxy: Optional[str] = None, timeout: Optional[int] = None) -> Dict[str, Any]:

        url_template = self.config.get("endpoints", {}).get("info")
        if not url_template:
            raise ValueError("'info' endpoint not configured for tencent source")

        # Tencent tickers need a market prefix, e.g., sh600519 or sz000001
        # Tencent API requires lower-case market prefix
        url = url_template.format(ticker=ticker.lower())

        try:
            response = self._data_fetcher.get(url, timeout=timeout)
            response.encoding = 'gbk' # As discovered from research
            response.raise_for_status()
            text = response.text
        except Exception:
            return {} # Return empty dict on failure

        # Example response: v_sh600519="1~贵州茅台~600519~1655.00~...~1598.00";
        match = re.search(r'"(.*)"', text)
        if not match:
            return {}

        parts = match.group(1).split('~')
        if len(parts) < 47:
            return {}

        try:
            # Map by index based on the CSDN blog post and other sources
            info = {
                "shortName": parts[1],
                "symbol": ticker,
                "currentPrice": float(parts[3]) if parts[3] else None,
                "previousClose": float(parts[4]) if parts[4] else None,
                "open": float(parts[5]) if parts[5] else None,
                "volume": int(parts[6]) * 100 if parts[6] else None, # In lots, convert to shares
                "high": float(parts[33]) if parts[33] else None,
                "low": float(parts[34]) if parts[34] else None,
                "turnover": float(parts[37]) * 10000 if parts[37] else None, # In 10k CNY, convert to CNY
                "turnoverRate": float(parts[38]) if parts[38] else None,
                "peRatio": float(parts[39]) if parts[39] else None,
                "pbRatio": float(parts[46]) if parts[46] else None,
                "marketCap": float(parts[45]) * 100000000 if parts[45] else None, # In 100 millions CNY
            }
            # Add a 'currency' field for compatibility
            info['currency'] = 'CNY'
            return info
        except (ValueError, IndexError):
            # Return empty dict on parsing errors
            return {}
