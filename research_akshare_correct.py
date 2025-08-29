#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
AKShare API 研究脚本 - 修正版

使用正确的 AKShare API 名称和参数
"""

import akshare as ak
import pandas as pd

def research_correct_akshare_apis():
    """研究 AKShare 的正确 API 功能"""
    
    print("=== AKShare API 正确用法研究 ===\n")
    
    # 1. 股票基本信息
    print("1. 股票基本信息获取:")
    try:
        info = ak.stock_individual_info_em(symbol="000001")
        print(f"   字段: {list(info.columns)}")
        print(f"   示例:\n{info.head()}")
    except Exception as e:
        print(f"   失败: {e}")
    
    print("\n" + "="*50)
    
    # 2. 历史价格数据
    print("2. 历史价格数据:")
    try:
        hist = ak.stock_zh_a_hist(symbol="000001", period="daily", start_date="20240801", end_date="20240810", adjust="")
        print(f"   字段: {list(hist.columns)}")
        print(f"   示例:\n{hist.head()}")
    except Exception as e:
        print(f"   失败: {e}")
    
    print("\n" + "="*50)
    
    # 3. 分红配股信息
    print("3. 分红配股信息:")
    try:
        # 正确的分红数据API
        dividends = ak.stock_dividend_individual(stock="000001")
        print(f"   字段: {list(dividends.columns)}")
        print(f"   示例:\n{dividends.head()}")
    except Exception as e:
        print(f"   失败: {e}")
    
    print("\n" + "="*50)
    
    # 4. 财务数据 - 利润表
    print("4. 利润表数据:")
    try:
        financials = ak.stock_financial_abstract_ths(symbol="000001", indicator="利润表")
        print(f"   字段: {list(financials.columns)}")
        print(f"   示例:\n{financials.head()}")
    except Exception as e:
        print(f"   失败: {e}")
    
    print("\n" + "="*50)
    
    # 5. 资产负债表
    print("5. 资产负债表:")
    try:
        balance = ak.stock_financial_abstract_ths(symbol="000001", indicator="资产负债表")
        print(f"   字段: {list(balance.columns)}")
        print(f"   示例:\n{balance.head()}")
    except Exception as e:
        print(f"   失败: {e}")
    
    print("\n" + "="*50)
    
    # 6. 现金流量表
    print("6. 现金流量表:")
    try:
        cashflow = ak.stock_financial_abstract_ths(symbol="000001", indicator="现金流量表")
        print(f"   字段: {list(cashflow.columns)}")
        print(f"   示例:\n{cashflow.head()}")
    except Exception as e:
        print(f"   失败: {e}")
    
    print("\n" + "="*50)
    
    # 7. 股东持股信息
    print("7. 股东持股信息:")
    try:
        holders = ak.stock_zh_a_gdhs(symbol="000001")
        print(f"   字段: {list(holders.columns)}")
        print(f"   示例:\n{holders.head()}")
    except Exception as e:
        print(f"   失败: {e}")
    
    print("\n" + "="*50)
    
    # 8. 新闻信息
    print("8. 新闻信息:")
    try:
        news = ak.stock_news_em(symbol="000001")
        print(f"   字段: {list(news.columns)}")
        print(f"   示例:\n{news.head()}")
    except Exception as e:
        print(f"   失败: {e}")

def get_available_apis():
    """获取可用的 API 列表"""
    print("\n=== 可用的 AKShare API 函数 ===")
    
    # 获取所有以 stock_ 开头的函数
    stock_funcs = [attr for attr in dir(ak) if attr.startswith('stock_') and callable(getattr(ak, attr))]
    
    print(f"共找到 {len(stock_funcs)} 个股票相关函数:")
    for i, func in enumerate(stock_funcs[:20], 1):  # 只显示前20个
        print(f"{i:2d}. {func}")
    
    if len(stock_funcs) > 20:
        print(f"... 还有 {len(stock_funcs) - 20} 个函数")

if __name__ == "__main__":
    research_correct_akshare_apis()
    get_available_apis()
