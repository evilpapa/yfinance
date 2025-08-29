#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
数据源集成验证脚本

验证多数据源架构的功能和兼容性，包括：
1. 数据源自动选择
2. 数据获取功能
3. 格式兼容性
4. 错误处理
"""

import sys
import os
import warnings
from datetime import datetime
import pandas as pd

# 添加项目路径到 Python 路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# 导入我们的新架构
from yfinance.datasources import get_data_source, list_available_sources, is_source_available
from yfinance.enhanced_ticker import MultiSourceTicker, create_ticker


def print_section(title: str):
    """打印节标题"""
    print(f"\n{'='*60}")
    print(f" {title}")
    print(f"{'='*60}")


def print_subsection(title: str):
    """打印子节标题"""
    print(f"\n{'-'*40}")
    print(f" {title}")
    print(f"{'-'*40}")


def test_data_source_factory():
    """测试数据源工厂"""
    print_section("数据源工厂测试")
    
    # 列出可用数据源
    available_sources = list_available_sources()
    print(f"可用数据源: {available_sources}")
    
    # 测试数据源可用性
    for source in ['yahoo', 'akshare']:
        available = is_source_available(source)
        print(f"{source} 数据源可用: {available}")
    
    # 测试自动数据源选择
    test_cases = [
        ("AAPL", "Yahoo Finance"),  # 美股
        ("000001", "AKShare"),      # A股
        ("TSLA", "Yahoo Finance"),  # 美股
        ("600036", "AKShare"),      # A股
    ]
    
    print_subsection("自动数据源选择测试")
    for ticker, expected_source in test_cases:
        try:
            data_source = get_data_source(ticker)
            actual_source = data_source.get_source_name()
            status = "✅" if expected_source in actual_source else "❌"
            print(f"{status} {ticker}: 期望 {expected_source}, 实际 {actual_source}")
        except Exception as e:
            print(f"❌ {ticker}: 错误 - {e}")


def test_yahoo_finance_integration():
    """测试 Yahoo Finance 集成"""
    print_section("Yahoo Finance 数据源测试")
    
    ticker = "AAPL"
    
    try:
        # 创建数据源
        data_source = get_data_source(ticker, preferred_source='yahoo')
        print(f"数据源: {data_source.get_source_name()}")
        
        # 测试基础信息
        print_subsection("基础信息测试")
        info = data_source.get_info()
        if info and 'symbol' in info:
            print(f"✅ 基础信息获取成功")
            print(f"   公司名称: {info.get('longName', 'N/A')}")
            print(f"   货币: {info.get('currency', 'N/A')}")
            print(f"   市值: {info.get('marketCap', 'N/A')}")
        else:
            print("❌ 基础信息获取失败")
        
        # 测试历史数据
        print_subsection("历史数据测试")
        history = data_source.get_history(period="5d", interval="1d")
        if not history.empty:
            print(f"✅ 历史数据获取成功，共 {len(history)} 条记录")
            print(f"   列名: {list(history.columns)}")
            print(f"   最新价格: {history['Close'].iloc[-1]:.2f}")
        else:
            print("❌ 历史数据获取失败")
        
        # 测试财务数据
        print_subsection("财务数据测试")
        financials = data_source.get_financials()
        if not financials.empty:
            print(f"✅ 财务数据获取成功，共 {financials.shape[0]} 个报告期")
            print(f"   财务指标数: {financials.shape[1]}")
        else:
            print("❌ 财务数据获取失败")
        
        # 测试新闻
        print_subsection("新闻数据测试")
        news = data_source.get_news(count=3)
        if news:
            print(f"✅ 新闻数据获取成功，共 {len(news)} 条")
            for i, news_item in enumerate(news[:2], 1):
                print(f"   {i}. {news_item.get('title', 'N/A')[:50]}...")
        else:
            print("❌ 新闻数据获取失败")
        
    except Exception as e:
        print(f"❌ Yahoo Finance 测试失败: {e}")


def test_akshare_integration():
    """测试 AKShare 集成"""
    print_section("AKShare 数据源测试")
    
    # 检查 AKShare 是否可用
    if not is_source_available('akshare'):
        print("⚠️  AKShare 不可用，跳过测试")
        return
    
    ticker = "000001"  # 平安银行
    
    try:
        # 创建数据源
        data_source = get_data_source(ticker, preferred_source='akshare')
        print(f"数据源: {data_source.get_source_name()}")
        
        # 测试基础信息
        print_subsection("基础信息测试")
        info = data_source.get_info()
        if info and 'symbol' in info:
            print(f"✅ 基础信息获取成功")
            print(f"   股票简称: {info.get('longName', 'N/A')}")
            print(f"   货币: {info.get('currency', 'N/A')}")
            print(f"   交易所: {info.get('exchange', 'N/A')}")
        else:
            print("❌ 基础信息获取失败")
        
        # 测试历史数据
        print_subsection("历史数据测试")
        history = data_source.get_history(period="5d", interval="1d")
        if not history.empty:
            print(f"✅ 历史数据获取成功，共 {len(history)} 条记录")
            print(f"   列名: {list(history.columns)}")
            print(f"   最新价格: {history['Close'].iloc[-1]:.2f}")
        else:
            print("❌ 历史数据获取失败")
        
        # 测试财务数据
        print_subsection("财务数据测试")
        financials = data_source.get_financials()
        if not financials.empty:
            print(f"✅ 财务数据获取成功，共 {financials.shape[0]} 个报告期")
            print(f"   财务指标数: {financials.shape[1]}")
        else:
            print("❌ 财务数据获取失败")
        
        # 测试新闻
        print_subsection("新闻数据测试")
        news = data_source.get_news(count=3)
        if news:
            print(f"✅ 新闻数据获取成功，共 {len(news)} 条")
            for i, news_item in enumerate(news[:2], 1):
                print(f"   {i}. {news_item.get('title', 'N/A')[:50]}...")
        else:
            print("❌ 新闻数据获取失败")
        
    except Exception as e:
        print(f"❌ AKShare 测试失败: {e}")


def test_enhanced_ticker():
    """测试增强版 Ticker"""
    print_section("增强版 Ticker 测试")
    
    test_cases = [
        ("AAPL", "美股测试"),
        ("000001", "A股测试"),
    ]
    
    for ticker, description in test_cases:
        print_subsection(description)
        
        try:
            # 创建增强版 Ticker
            stock = create_ticker(ticker)
            print(f"✅ {stock}")
            
            # 测试基础属性
            info = stock.info
            if info and 'symbol' in info:
                print(f"   公司名称: {info.get('longName', 'N/A')}")
                print(f"   数据源: {stock.source_name}")
            
            # 测试历史数据方法
            history = stock.history(period="5d")
            if not history.empty:
                print(f"   历史数据: {len(history)} 条记录")
            
            # 测试属性访问
            try:
                dividends = stock.dividends
                print(f"   股息记录: {len(dividends)} 条")
            except:
                print("   股息记录: 不可用")
            
        except Exception as e:
            print(f"❌ {description} 失败: {e}")


def test_compatibility():
    """测试向后兼容性"""
    print_section("向后兼容性测试")
    
    # 测试与原版 yfinance 的兼容性
    try:
        from yfinance import Ticker as OriginalTicker
        
        ticker = "AAPL"
        
        # 原版 Ticker
        print_subsection("原版 Ticker")
        original_stock = OriginalTicker(ticker)
        print(f"✅ 原版 Ticker 创建成功: {original_stock}")
        
        # 增强版 Ticker
        print_subsection("增强版 Ticker")
        enhanced_stock = create_ticker(ticker)
        print(f"✅ 增强版 Ticker 创建成功: {enhanced_stock}")
        
        # 比较接口兼容性
        print_subsection("接口兼容性比较")
        common_methods = ['info', 'history', 'dividends', 'splits', 'financials']
        
        for method in common_methods:
            original_has = hasattr(original_stock, method)
            enhanced_has = hasattr(enhanced_stock, method)
            status = "✅" if original_has == enhanced_has else "❌"
            print(f"{status} {method}: 原版={original_has}, 增强版={enhanced_has}")
        
    except ImportError:
        print("⚠️  原版 yfinance 不可用，跳过兼容性测试")
    except Exception as e:
        print(f"❌ 兼容性测试失败: {e}")


def main():
    """主测试函数"""
    print("yfinance 多数据源架构验证")
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 执行各项测试
    test_data_source_factory()
    test_yahoo_finance_integration()
    test_akshare_integration()
    test_enhanced_ticker()
    test_compatibility()
    
    print_section("测试完成")
    print("验证脚本执行完毕。请检查上述结果确认集成状态。")
    print("\n使用示例:")
    print("```python")
    print("from yfinance.enhanced_ticker import create_ticker")
    print("")
    print("# 自动选择数据源")
    print("aapl = create_ticker('AAPL')  # 使用 Yahoo Finance")
    print("ping_an = create_ticker('000001')  # 使用 AKShare")
    print("")
    print("# 手动指定数据源")
    print("aapl_yahoo = create_ticker('AAPL', preferred_source='yahoo')")
    print("ping_an_akshare = create_ticker('000001', preferred_source='akshare')")
    print("")
    print("# 获取数据")
    print("print(aapl.info)")
    print("print(aapl.history(period='1mo'))")
    print("```")


if __name__ == "__main__":
    # 设置警告过滤
    warnings.filterwarnings('ignore', category=UserWarning)
    warnings.filterwarnings('ignore', category=FutureWarning)
    
    main()
