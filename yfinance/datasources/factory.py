from typing import Dict, Any, Optional, List

from .base import DataSourceStrategy
from .generic import GenericDataSource
from .yahoo import YahooDataSource
from .tencent import TencentDataSource

class DataSourceFactory:
    """
    A factory for creating and managing data source strategies.
    This acts as a central registry for all available data sources.
    """
    _registry: Dict[str, Dict[str, Any]] = {}
    _default_source_name: str = "yahoo"  # Default to yahoo

    @classmethod
    def register_source(cls, name: str, config: Dict[str, Any]):
        """
        Registers a new data source configuration.

        :param name: The name of the data source (e.g., 'yahoo', 'tencent').
        :param config: The configuration dictionary for this source.
        """
        cls._registry[name] = config

    @classmethod
    def get_source(cls, name: Optional[str] = None) -> DataSourceStrategy:
        """
        Retrieves a configured data source strategy instance.

        :param name: The name of the data source to retrieve. If None,
                     the default source is returned.
        :return: An instance of a class that implements DataSourceStrategy.
        """
        if name is None:
            name = cls._default_source_name

        if name not in cls._registry:
            raise ValueError(f"Data source '{name}' is not registered. "
                             f"Available sources: {list(cls._registry.keys())}")

        config = cls._registry[name]

        if name == 'yahoo':
            return YahooDataSource(config)
        elif name == 'tencent':
            return TencentDataSource(config)

        # Default to GenericDataSource for any other source
        return GenericDataSource(config)

    @classmethod
    def set_default(cls, name: str):
        """
        Sets the default data source name.

        :param name: The name of the data source to set as default.
        """
        if name not in cls._registry:
            # If we are setting a default, it must be registered first.
            # However, we might want to register it later.
            # For now, let's enforce registration first.
            raise ValueError(f"Cannot set default source to '{name}' because it is not registered.")
        cls._default_source_name = name

    @classmethod
    def get_available_sources(cls) -> List[str]:
        """Returns a list of available source names."""
        return list(cls._registry.keys())
