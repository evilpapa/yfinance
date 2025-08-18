import pandas as pd
from typing import Dict, Any, Optional
import warnings
import json

from .base import DataSourceStrategy
from .generic import GenericDataSource
from ..data import YfData
from ..const import _BASE_URL_, _QUERY1_URL_
from ..exceptions import YFDataException, YFException
from .. import utils

_QUOTE_SUMMARY_URL_ = f"{_BASE_URL_}/v10/finance/quoteSummary"

class YahooDataSource(GenericDataSource):
    """
    Data source for fetching data from Yahoo Finance.
    This class overrides methods from GenericDataSource where Yahoo's
    data fetching or parsing is too complex for a generic config-based approach.
    """

    def get_info(self, ticker: str, proxy: Optional[str] = None, timeout: Optional[int] = None) -> Dict[str, Any]:
        """
        Fetches, parses, and formats the 'info' data for a ticker from Yahoo Finance.
        This logic is migrated from the old scraper to ensure full compatibility.
        """

        # Step 1: Fetch data from multiple endpoints
        modules = ['financialData', 'quoteType', 'defaultKeyStatistics', 'assetProfile', 'summaryDetail']
        params_dict = {"modules": ",".join(modules)}

        # Use the internal _data_fetcher from the parent class
        try:
            summary_result = self._data_fetcher.get_raw_json(_QUOTE_SUMMARY_URL_ + f"/{ticker}", params=params_dict)
        except Exception:
            summary_result = None

        try:
            quote_result = self._data_fetcher.get_raw_json(f"{_QUERY1_URL_}/v7/finance/quote?", params={"symbols": ticker})
        except Exception:
            quote_result = None

        # Step 2: Combine and process the JSON data
        info = {}
        if summary_result is not None:
            info.update(summary_result)
        if quote_result is not None:
            info.update(quote_result)

        if not info:
            return {}

        processed_info = {}
        for quote in ["quoteSummary", "quoteResponse"]:
            if quote in info and len(info[quote]["result"]) > 0:
                info[quote]["result"][0]["symbol"] = ticker
                query_info = next(
                    (res for res in info.get(quote, {}).get("result", [])
                    if res.get("symbol") == ticker),
                    None,
                )
                if query_info:
                    processed_info.update(query_info)

        # Step 3: Flatten the processed data
        flattened_info = {}
        for k, v in processed_info.items():
            if isinstance(v, dict):
                flattened_info.update(v)
            else:
                flattened_info[k] = v

        # Step 4: Final formatting (simplified from original)
        final_info = {}
        for k, v in flattened_info.items():
            if isinstance(v, dict) and "raw" in v:
                final_info[k] = v["raw"]
            elif v is not None:
                final_info[k] = v

        # Add symbol back in just in case it was missed
        if 'symbol' not in final_info:
            final_info['symbol'] = ticker

        return final_info
