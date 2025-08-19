from typing import Dict, Any, Optional, List, Type
from .base import DataSourceStrategy

class DataSourceFactory:
    """
    一个用于创建和管理数据源策略的工厂类。
    A factory for creating and managing data source strategies.

    这个类扮演着一个中心注册表(central registry)的角色，所有可用的数据源都需要在这里注册。
    它允许用户在运行时动态地切换数据源。
    """
    _source_classes: Dict[str, Type[DataSourceStrategy]] = {}
    _default_source_name: str = "yahoo"  # 默认数据源为 'yahoo'

    @classmethod
    def register_source(cls, name: str, source_class: Type[DataSourceStrategy]):
        """
        注册一个新的数据源策略类。
        Registers a new data source strategy class.

        :param name: 数据源的名称 (e.g., 'yahoo', 'akshare').
        :param source_class: 实现了 DataSourceStrategy 接口的类。
        """
        cls._source_classes[name] = source_class

    @classmethod
    def get_source(cls, name: Optional[str] = None) -> DataSourceStrategy:
        """
        根据名称获取一个数据源策略的实例。
        Retrieves a configured data source strategy instance by name.

        :param name: 要获取的数据源的名称。如果为 None，则返回默认数据源。
        :return: 一个实现了 DataSourceStrategy 接口的类的实例。
        """
        if name is None:
            name = cls._default_source_name

        source_class = cls._source_classes.get(name)
        if not source_class:
            raise ValueError(f"数据源 '{name}' 未被注册。可用数据源: {list(cls._source_classes.keys())}")

        # 实例化策略类
        return source_class()

    @classmethod
    def set_default(cls, name: str):
        """
        设置默认的数据源。
        Sets the default data source.

        :param name: 要设置为默认的数据源的名称。
        """
        if name not in cls._source_classes:
            raise ValueError(f"无法将 '{name}' 设置为默认数据源，因为它尚未被注册。")
        cls._default_source_name = name

    @classmethod
    def get_available_sources(cls) -> List[str]:
        """
        返回所有可用的数据源名称列表。
        Returns a list of available source names.
        """
        return list(cls._source_classes.keys())
