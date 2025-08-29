#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
数据源工厂类

该模块实现了工厂模式，用于管理和创建不同的数据源实例。
支持数据源的注册、自动选择和配置。
"""

import re
from typing import Dict, Type, Optional, List, Union
from .base import DataSourceStrategy


class DataSourceFactory:
    """
    数据源工厂类
    
    负责管理各种数据源的注册和创建。支持：
    1. 自动根据股票代码选择合适的数据源
    2. 手动指定数据源
    3. 数据源的注册和注销
    4. 配置管理
    """

    # 注册的数据源类
    _datasources: Dict[str, Type[DataSourceStrategy]] = {}
    
    # 市场代码模式匹配
    _market_patterns: Dict[str, List[str]] = {}
    
    # 默认数据源
    _default_source: str = "yahoo"
    
    # 配置选项
    _config: Dict[str, Union[str, bool, int]] = {
        "auto_select": True,  # 是否自动选择数据源
        "fallback_enabled": True,  # 是否启用备选数据源
        "cache_enabled": True,  # 是否启用缓存
        "timeout": 30,  # 请求超时时间
        "retry_count": 3,  # 重试次数
        "prefer_local": False,  # 是否优先使用本地数据源
    }

    @classmethod
    def register_datasource(
        cls, 
        name: str, 
        datasource_class: Type[DataSourceStrategy],
        market_patterns: Optional[List[str]] = None
    ) -> None:
        """
        注册数据源
        
        Args:
            name: 数据源名称
            datasource_class: 数据源类
            market_patterns: 该数据源支持的股票代码模式列表
        """
        if not issubclass(datasource_class, DataSourceStrategy):
            raise ValueError(f"数据源类 {datasource_class} 必须继承 DataSourceStrategy")
        
        cls._datasources[name] = datasource_class
        
        if market_patterns:
            cls._market_patterns[name] = market_patterns
        
        print(f"数据源 '{name}' 注册成功")

    @classmethod
    def unregister_datasource(cls, name: str) -> None:
        """
        注销数据源
        
        Args:
            name: 数据源名称
        """
        if name in cls._datasources:
            del cls._datasources[name]
        if name in cls._market_patterns:
            del cls._market_patterns[name]
        print(f"数据源 '{name}' 注销成功")

    @classmethod
    def get_registered_datasources(cls) -> List[str]:
        """
        获取已注册的数据源列表
        
        Returns:
            List[str]: 数据源名称列表
        """
        return list(cls._datasources.keys())

    @classmethod
    def set_default_datasource(cls, name: str) -> None:
        """
        设置默认数据源
        
        Args:
            name: 数据源名称
        """
        if name not in cls._datasources:
            raise ValueError(f"数据源 '{name}' 未注册")
        
        cls._default_source = name
        print(f"默认数据源设置为: {name}")

    @classmethod
    def get_default_datasource(cls) -> str:
        """
        获取默认数据源名称
        
        Returns:
            str: 默认数据源名称
        """
        return cls._default_source

    @classmethod
    def auto_select_datasource(cls, ticker: str) -> str:
        """
        根据股票代码自动选择数据源
        
        Args:
            ticker: 股票代码
            
        Returns:
            str: 选择的数据源名称
        """
        ticker = ticker.upper().strip()
        
        # 中国A股市场模式
        china_patterns = [
            r'^\d{6}$',  # 6位数字：000001, 600000 等
            r'^(0|3|6|8|9)\d{5}$',  # 特定开头的6位数字
        ]
        
        # 检查是否为中国A股
        for pattern in china_patterns:
            if re.match(pattern, ticker):
                if "akshare" in cls._datasources:
                    return "akshare"
        
        # 美股和其他国际市场模式
        international_patterns = [
            r'^[A-Z]{1,5}$',  # 1-5个字母：AAPL, GOOGL 等
            r'^[A-Z]+\.[A-Z]{1,3}$',  # 带后缀：TSM.TO, ASML.AS 等
            r'^\^[A-Z0-9]+$',  # 指数：^GSPC, ^DJI 等
        ]
        
        # 检查是否为国际市场
        for pattern in international_patterns:
            if re.match(pattern, ticker):
                if "yahoo" in cls._datasources:
                    return "yahoo"
        
        # 使用自定义模式匹配
        for source_name, patterns in cls._market_patterns.items():
            for pattern in patterns:
                if re.match(pattern, ticker):
                    return source_name
        
        # 返回默认数据源
        return cls._default_source

    @classmethod
    def create_datasource(
        cls, 
        ticker: str, 
        source: Optional[str] = None,
        **kwargs
    ) -> DataSourceStrategy:
        """
        创建数据源实例
        
        Args:
            ticker: 股票代码
            source: 指定的数据源名称，如果为 None 则自动选择
            **kwargs: 传递给数据源构造函数的额外参数
            
        Returns:
            DataSourceStrategy: 数据源实例
            
        Raises:
            ValueError: 如果数据源不存在或创建失败
        """
        # 自动选择数据源
        if source is None and cls._config["auto_select"]:
            source = cls.auto_select_datasource(ticker)
        elif source is None:
            source = cls._default_source
        
        # 检查数据源是否存在
        if source not in cls._datasources:
            available = list(cls._datasources.keys())
            raise ValueError(
                f"数据源 '{source}' 不存在。可用的数据源: {available}"
            )
        
        # 创建数据源实例
        try:
            datasource_class = cls._datasources[source]
            instance = datasource_class(ticker, **kwargs)
            
            # 验证数据源是否支持该股票代码
            if hasattr(instance, 'supports_ticker'):
                if not instance.supports_ticker(ticker):
                    if cls._config["fallback_enabled"]:
                        # 尝试使用备选数据源
                        fallback_source = cls._get_fallback_source(source)
                        if fallback_source:
                            print(f"数据源 '{source}' 不支持 '{ticker}'，使用备选数据源 '{fallback_source}'")
                            return cls.create_datasource(ticker, fallback_source, **kwargs)
                    
                    raise ValueError(f"数据源 '{source}' 不支持股票代码 '{ticker}'")
            
            return instance
            
        except Exception as e:
            if cls._config["fallback_enabled"]:
                # 尝试使用备选数据源
                fallback_source = cls._get_fallback_source(source)
                if fallback_source:
                    print(f"数据源 '{source}' 创建失败: {e}")
                    print(f"尝试使用备选数据源 '{fallback_source}'")
                    return cls.create_datasource(ticker, fallback_source, **kwargs)
            
            raise ValueError(f"创建数据源 '{source}' 失败: {e}")

    @classmethod
    def _get_fallback_source(cls, failed_source: str) -> Optional[str]:
        """
        获取备选数据源
        
        Args:
            failed_source: 失败的数据源名称
            
        Returns:
            Optional[str]: 备选数据源名称，如果没有则返回 None
        """
        available_sources = [name for name in cls._datasources.keys() if name != failed_source]
        
        if not available_sources:
            return None
        
        # 优先选择默认数据源
        if cls._default_source in available_sources:
            return cls._default_source
        
        # 返回第一个可用的数据源
        return available_sources[0]

    @classmethod
    def set_config(cls, **kwargs) -> None:
        """
        设置配置选项
        
        Args:
            **kwargs: 配置参数
                auto_select: 是否自动选择数据源
                fallback_enabled: 是否启用备选数据源
                cache_enabled: 是否启用缓存
                timeout: 请求超时时间
                retry_count: 重试次数
                prefer_local: 是否优先使用本地数据源
        """
        for key, value in kwargs.items():
            if key in cls._config:
                cls._config[key] = value
                print(f"配置 '{key}' 设置为: {value}")
            else:
                print(f"警告: 未知的配置选项 '{key}'")

    @classmethod
    def get_config(cls, key: Optional[str] = None) -> Union[Dict, any]:
        """
        获取配置选项
        
        Args:
            key: 配置键名，如果为 None 则返回所有配置
            
        Returns:
            Union[Dict, any]: 配置值或配置字典
        """
        if key is None:
            return cls._config.copy()
        return cls._config.get(key)

    @classmethod
    def reset_config(cls) -> None:
        """重置配置为默认值"""
        cls._config = {
            "auto_select": True,
            "fallback_enabled": True,
            "cache_enabled": True,
            "timeout": 30,
            "retry_count": 3,
            "prefer_local": False,
        }
        print("配置已重置为默认值")

    @classmethod
    def get_datasource_info(cls, name: str) -> Dict:
        """
        获取数据源信息
        
        Args:
            name: 数据源名称
            
        Returns:
            Dict: 数据源信息
        """
        if name not in cls._datasources:
            raise ValueError(f"数据源 '{name}' 不存在")
        
        datasource_class = cls._datasources[name]
        
        info = {
            "name": name,
            "class": datasource_class.__name__,
            "module": datasource_class.__module__,
            "patterns": cls._market_patterns.get(name, []),
            "is_default": name == cls._default_source,
        }
        
        # 尝试获取支持的市场信息
        try:
            temp_instance = datasource_class("TEMP")
            if hasattr(temp_instance, 'get_supported_markets'):
                info["supported_markets"] = temp_instance.get_supported_markets()
            if hasattr(temp_instance, 'get_source_name'):
                info["source_name"] = temp_instance.get_source_name()
        except:
            pass
        
        return info

    @classmethod
    def list_datasources(cls) -> None:
        """打印所有已注册数据源的信息"""
        print("\n=== 已注册的数据源 ===")
        
        if not cls._datasources:
            print("没有注册的数据源")
            return
        
        for name in cls._datasources:
            try:
                info = cls.get_datasource_info(name)
                print(f"\n数据源: {name}")
                print(f"  类名: {info['class']}")
                print(f"  模块: {info['module']}")
                print(f"  默认: {'是' if info['is_default'] else '否'}")
                if info.get('patterns'):
                    print(f"  模式: {info['patterns']}")
                if info.get('supported_markets'):
                    print(f"  支持市场: {info['supported_markets']}")
            except Exception as e:
                print(f"\n数据源: {name} (获取信息失败: {e})")

    @classmethod
    def clear_all(cls) -> None:
        """清除所有注册的数据源"""
        cls._datasources.clear()
        cls._market_patterns.clear()
        print("所有数据源已清除")


# 创建默认工厂实例
factory = DataSourceFactory()
