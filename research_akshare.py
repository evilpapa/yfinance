#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
AKShare API 研究脚本

本脚本用于调研 AKShare 的功能，找到与 yfinance 核心功能对应的实现。
"""

import akshare as ak
import pandas as pd
from datetime import datetime, timedelta

def research_akshare_apis():
    """研究 AKShare 的主要 API 功能"""
    
    print("=== AKShare API 功能研究 ===\n")
    
    # 1. 股票基本信息
    print("1. 股票基本信息获取:")
    try:
        # 获取股票基本信息 - 对应 yfinance 的 get_info()
        info = ak.stock_individual_info_em(symbol="000001")
        print(f"   股票信息字段: {list(info.columns) if hasattr(info, 'columns') else 'Not DataFrame'}")
        print(f"   示例数据: {info.head(3) if hasattr(info, 'head') else info}")
    except Exception as e:
        print(f"   获取股票信息失败: {e}")
    
    print("\n" + "="*50)
    
    # 2. 历史价格数据
    print("2. 历史价格数据:")
    try:
        # 获取历史价格 - 对应 yfinance 的 history()
        hist = ak.stock_zh_a_hist(symbol="000001", period="daily", start_date="20240101", end_date="20240131", adjust="")
        print(f"   历史数据字段: {list(hist.columns)}")
        print(f"   数据样本:\n{hist.head(3)}")
    except Exception as e:
        print(f"   获取历史数据失败: {e}")
    
    print("\n" + "="*50)
    
    # 3. 股息分红信息
    print("3. 股息分红信息:")
    try:
        # 获取分红配股数据 - 对应 yfinance 的 get_dividends()
        dividends = ak.stock_fh_xq(symbol="000001")
        print(f"   分红数据字段: {list(dividends.columns)}")
        print(f"   分红样本:\n{dividends.head(3)}")
    except Exception as e:
        print(f"   获取分红数据失败: {e}")
    
    print("\n" + "="*50)
    
    # 4. 财务数据
    print("4. 财务报表数据:")
    try:
        # 获取利润表 - 对应 yfinance 的 get_financials()
        income_stmt = ak.stock_lrb_em(symbol="000001")
        print(f"   利润表字段: {list(income_stmt.columns)}")
        print(f"   利润表样本:\n{income_stmt.head(3)}")
    except Exception as e:
        print(f"   获取利润表失败: {e}")
    
    print("\n" + "="*50)
    
    # 5. 资产负债表
    print("5. 资产负债表:")
    try:
        # 获取资产负债表 - 对应 yfinance 的 get_balance_sheet()
        balance_sheet = ak.stock_zcfzb_em(symbol="000001")
        print(f"   资产负债表字段: {list(balance_sheet.columns)}")
        print(f"   资产负债表样本:\n{balance_sheet.head(3)}")
    except Exception as e:
        print(f"   获取资产负债表失败: {e}")
    
    print("\n" + "="*50)
    
    # 6. 现金流量表
    print("6. 现金流量表:")
    try:
        # 获取现金流量表 - 对应 yfinance 的 get_cash_flow()
        cash_flow = ak.stock_xjllb_em(symbol="000001")
        print(f"   现金流量表字段: {list(cash_flow.columns)}")
        print(f"   现金流量表样本:\n{cash_flow.head(3)}")
    except Exception as e:
        print(f"   获取现金流量表失败: {e}")
    
    print("\n" + "="*50)
    
    # 7. 主要持股者信息
    print("7. 主要持股者信息:")
    try:
        # 获取股东信息 - 对应 yfinance 的 get_major_holders()
        holders = ak.stock_gdfx_holding_analyse_em(symbol="000001")
        print(f"   持股者数据字段: {list(holders.columns)}")
        print(f"   持股者样本:\n{holders.head(3)}")
    except Exception as e:
        print(f"   获取持股者信息失败: {e}")
    
    print("\n" + "="*50)
    
    # 8. 股票拆分信息
    print("8. 股票拆分/送股信息:")
    try:
        # 获取股本变动 - 对应 yfinance 的 get_splits()
        splits = ak.stock_fh_xq(symbol="000001")  # 包含送股信息
        print(f"   股本变动字段: {list(splits.columns)}")
        print(f"   股本变动样本:\n{splits.head(3)}")
    except Exception as e:
        print(f"   获取股本变动失败: {e}")

def create_mapping_table():
    """创建 yfinance 与 AKShare API 的映射表"""
    
    mapping = {
        "yfinance 方法": [
            "get_info()",
            "history()",
            "get_dividends()",
            "get_splits()",
            "get_financials() / get_income_stmt()",
            "get_balance_sheet()",
            "get_cash_flow()",
            "get_major_holders()",
            "get_institutional_holders()",
            "get_earnings()",
            "get_recommendations()",
            "get_news()",
            "get_sustainability()",
            "get_analyst_price_targets()"
        ],
        "AKShare 对应方法": [
            "stock_individual_info_em()",
            "stock_zh_a_hist()",
            "stock_fh_xq() - 分红部分",
            "stock_fh_xq() - 送股部分",
            "stock_lrb_em()",
            "stock_zcfzb_em()",
            "stock_xjllb_em()",
            "stock_gdfx_holding_analyse_em()",
            "stock_gdfx_holding_analyse_em() - 机构部分",
            "stock_lrb_em() - 净利润部分",
            "暂无直接对应",
            "stock_news_em()",
            "暂无直接对应",
            "暂无直接对应"
        ],
        "数据可用性": [
            "✅ 可用",
            "✅ 可用",
            "✅ 可用",
            "✅ 可用",
            "✅ 可用",
            "✅ 可用", 
            "✅ 可用",
            "✅ 可用",
            "⚠️ 部分可用",
            "✅ 可用",
            "❌ 不可用",
            "✅ 可用",
            "❌ 不可用",
            "❌ 不可用"
        ]
    }
    
    df = pd.DataFrame(mapping)
    print("\n=== yfinance 与 AKShare API 映射表 ===")
    print(df.to_string(index=False))
    
    return df

if __name__ == "__main__":
    # 进行 API 研究
    research_akshare_apis()
    
    # 创建映射表
    mapping_df = create_mapping_table()
    
    print("\n=== 总结 ===")
    print("AKShare 主要优势:")
    print("1. 专注中国股市数据，数据质量高")
    print("2. 提供丰富的A股财务数据")
    print("3. 免费获取实时和历史数据")
    print("4. 支持多种数据格式和周期")
    
    print("\nAKShare 局限性:")
    print("1. 主要支持中国市场，国际市场数据有限")
    print("2. 缺少分析师评级和目标价数据")
    print("3. 可持续性数据不可用")
    print("4. API 设计风格与 yfinance 有差异")
    
    print("\n集成策略建议:")
    print("1. 对于A股股票，优先使用 AKShare")
    print("2. 对于美股等国际股票，继续使用 Yahoo Finance")
    print("3. 实现智能路由，根据股票代码自动选择数据源")
    print("4. 提供统一的数据格式转换层")
