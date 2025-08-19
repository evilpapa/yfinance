# -*- coding: utf-8 -*-

import yfinance as yf
import json

print("--- 验证 yfinance 原有功能 (Yahoo) ---")
print("--> 数据源: yahoo (默认)")
goog = yf.Ticker('GOOGL')
print("--> 正在获取 GOOGL 的 info...")
info_yahoo = goog.info
assert 'marketCap' in info_yahoo, "雅虎数据源 info 测试失败: 缺少 'marketCap'"
print(f"成功获取 {info_yahoo.get('shortName')} 的信息。")
print("-" * 30)


print("\n--- 验证切换到 akshare 数据源并获取A股数据 ---")
print("--> 切换数据源至: akshare")
yf.set_data_source('akshare')

# 使用一个知名的A股股票代码, 例如贵州茅台 (600519)
stock_code_ak = '600519'
moutai = yf.Ticker(stock_code_ak)
print(f"--> 正在获取 {stock_code_ak} 的 info...")
info_ak = moutai.info

print(f"\n--- 从 akshare 获取的 {stock_code_ak} 信息 ---")
print(json.dumps(info_ak, indent=4, ensure_ascii=False))

# 验证关键字段是否存在并且格式正确
assert info_ak.get('shortName') == '贵州茅台', "akshare info 测试失败: 股票名称不匹配"
assert 'marketCap' in info_ak and info_ak['marketCap'] > 0, "akshare info 测试失败: 'marketCap' 字段缺失或无效"
assert info_ak.get('currency') == 'CNY', "akshare info 测试失败: 货币单位不正确"
print("\n--> akshare info 数据测试通过！")
print("-" * 30)

print(f"\n--- 验证 akshare 的 history 功能 ---")
print(f"--> 正在获取 {stock_code_ak} 的1个月历史数据...")
hist_ak = moutai.history(period="1mo")
print("从 akshare 获取的历史数据样本:")
print(hist_ak.head())

# 验证返回的数据是否符合 yfinance 的格式
assert not hist_ak.empty, "akshare history 测试失败: 返回的DataFrame为空"
assert 'Adj Close' in hist_ak.columns, "akshare history 测试失败: 缺少 'Adj Close' 列"
print("\n--> akshare history 数据测试通过！")
print("-" * 30)

print("\n所有验证成功完成！新架构工作正常。")
