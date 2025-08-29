#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
数据源模块

该模块包含所有可用的数据源适配器，用于从不同的金融数据提供商获取数据。
"""

from .base import DataSourceStrategy
from .factory import DataSourceFactory
from .yahoo_datasource import YahooDataSource

# 尝试导入 AKShare 数据源（如果 akshare 已安装）
try:
    from .akshare_datasource import AkshareDataSource
    _AKSHARE_AVAILABLE = True
except ImportError:
    AkshareDataSource = None
    _AKSHARE_AVAILABLE = False

# 导出所有数据源
__all__ = [
    'DataSourceStrategy',
    'DataSourceFactory', 
    'YahooDataSource',
]

# 如果 AKShare 可用，添加到导出列表
if _AKSHARE_AVAILABLE:
    __all__.append('AkshareDataSource')

# 创建默认工厂实例
default_factory = DataSourceFactory()

# 注册 Yahoo Finance 数据源
default_factory.register_source('yahoo', YahooDataSource)

# 如果 AKShare 可用，注册 AKShare 数据源
if _AKSHARE_AVAILABLE:
    default_factory.register_source('akshare', AkshareDataSource)

# 配置数据源优先级和模式匹配
default_factory.configure_patterns({
    r'^\d{6}$': 'akshare',  # 6位数字 -> AKShare (中国A股)
    r'.*': 'yahoo'          # 其他所有格式 -> Yahoo Finance
})

def get_data_source(ticker: str, preferred_source: str = None) -> DataSourceStrategy:
    """
    获取适合指定股票代码的数据源实例
    
    Args:
        ticker: 股票代码
        preferred_source: 首选数据源名称（可选）
        
    Returns:
        DataSourceStrategy: 数据源实例
        
    Raises:
        ValueError: 如果没有找到合适的数据源
    """
    return default_factory.get_source(ticker, preferred_source)

def list_available_sources() -> list:
    """
    列出所有可用的数据源
    
    Returns:
        list: 可用数据源名称列表
    """
    return default_factory.list_sources()

def is_source_available(source_name: str) -> bool:
    """
    检查指定数据源是否可用
    
    Args:
        source_name: 数据源名称
        
    Returns:
        bool: 如果可用则返回 True
    """
    return source_name in default_factory.list_sources()
