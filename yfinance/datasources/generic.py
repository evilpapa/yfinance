import pandas as pd
from typing import Dict, Any, Optional

from .base import DataSourceStrategy
from ..data import YfData

def _get_nested_val(data: Dict[str, Any], key_path: str) -> Optional[Any]:
    """
    Helper function to retrieve a nested value from a dict/list structure using a dot-separated path.
    e.g., _get_nested_val(data, "profile.city")
    e.g., _get_nested_val(data, "timeseries.result.0.trailingPegRatio.-1.reportedValue.raw")
    """
    keys = key_path.split('.')
    val = data
    for key in keys:
        if isinstance(val, dict) and key in val:
            val = val[key]
        elif isinstance(val, list) and key.lstrip('-').isdigit():
            try:
                val = val[int(key)]
            except IndexError:
                return None
        else:
            return None
    return val

class GenericDataSource(DataSourceStrategy):
    """
    A generic data source strategy that is configured through a dictionary.
    This allows adding new data sources without writing new code.
    """
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self._data_fetcher = YfData()  # Uses the singleton YfData for requests

    def get_info(self, ticker: str, proxy: Optional[str] = None, timeout: Optional[int] = None) -> Dict[str, Any]:
        """
        Fetches general information for a ticker using the configured endpoint and mapper.
        """
        endpoints = self.config.get("endpoints", {})
        mappers = self.config.get("mappers", {})

        endpoint_config = endpoints.get("info")
        if not endpoint_config:
            raise ValueError(f"'info' endpoint not configured for source '{self.config.get('name')}'")

        # Standardize endpoint_config to be a list
        if not isinstance(endpoint_config, list):
            endpoint_config = [endpoint_config]

        combined_raw_data = {}
        for config in endpoint_config:
            url_template = config.get("url")
            if not url_template:
                continue

            url = url_template.format(ticker=ticker)

            # Note: The YfData singleton manages proxy settings globally.
            # For simplicity in this generic class, we rely on that global setup.
            try:
                response = self._data_fetcher.get(url, timeout=timeout)
                response.raise_for_status()
                json_data = response.json()
            except Exception:  # Broad exception to handle various network/HTTP errors
                json_data = None

            if json_data:
                data_path = config.get("data_path")
                if data_path:
                    raw_data = _get_nested_val(json_data, data_path)
                else:
                    raw_data = json_data

                if raw_data:
                    # This assumes the data at data_path is a dictionary
                    if isinstance(raw_data, dict):
                        combined_raw_data.update(raw_data)

        if not combined_raw_data:
            return {}

        raw_data = combined_raw_data

        info_map = mappers.get("info", {})
        result = {}
        for yf_field, source_field in info_map.items():
            value = _get_nested_val(raw_data, source_field)
            if value is not None:
                # The source might return empty dicts/lists for missing data
                if isinstance(value, (dict, list)) and not value:
                    continue
                result[yf_field] = value

        return result

    # The following methods are not implemented yet, but are required by the ABC.
    # They will be implemented in subsequent steps of the refactoring.

    def get_history(self, ticker: str, period: str, interval: str,
                    start: Optional[str] = None, end: Optional[str] = None,
                    prepost: bool = False, actions: bool = True,
                    auto_adjust: bool = True, back_adjust: bool = False,
                    proxy: Optional[str] = None, rounding: bool = False,
                    tz: Optional[str] = None, timeout: Optional[int] = None,
                    **kwargs) -> Optional[pd.DataFrame]:
        """Fetches historical market data."""
        raise NotImplementedError

    def get_major_holders(self, ticker: str, proxy: Optional[str] = None, timeout: Optional[int] = None) -> Optional[pd.DataFrame]:
        """Fetches major holders data."""
        raise NotImplementedError

    def get_institutional_holders(self, ticker: str, proxy: Optional[str] = None, timeout: Optional[int] = None) -> Optional[pd.DataFrame]:
        """Fetches institutional holders data."""
        raise NotImplementedError

    def get_income_stmt(self, ticker: str, proxy: Optional[str] = None, timeout: Optional[int] = None,
                          freq: str = "yearly") -> Optional[pd.DataFrame]:
        """Fetches income statement."""
        raise NotImplementedError

    def get_balance_sheet(self, ticker: str, proxy: Optional[str] = None, timeout: Optional[int] = None,
                            freq: str = "yearly") -> Optional[pd.DataFrame]:
        """Fetches balance sheet."""
        raise NotImplementedError

    def get_cash_flow(self, ticker: str, proxy: Optional[str] = None, timeout: Optional[int] = None,
                        freq: str = "yearly") -> Optional[pd.DataFrame]:
        """Fetches cash flow statement."""
        raise NotImplementedError

    def get_recommendations(self, ticker: str, proxy: Optional[str] = None, timeout: Optional[int] = None) -> Optional[pd.DataFrame]:
        """Fetches analyst recommendations."""
        raise NotImplementedError

    def get_earnings_dates(self, ticker: str, proxy: Optional[str] = None, timeout: Optional[int] = None) -> Optional[pd.DataFrame]:
        """Fetches earnings dates."""
        raise NotImplementedError
