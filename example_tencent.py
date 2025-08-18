# -*- coding: utf-8 -*-

import yfinance as yf
import json

print("--> Switching data source to 'tencent'")
yf.set_data_source('tencent')

# Tickers for Tencent need to be in the format 'market_code' + 'stock_code'
# e.g., 'sh600519' for Kweichow Moutai (贵州茅台) on the Shanghai exchange.
#      'sz000001' for Ping An Bank (平安银行) on the Shenzhen exchange.
ticker_symbol = 'sh600519'
print(f"--> Fetching info for {ticker_symbol} using Tencent source...")

try:
    stock = yf.Ticker(ticker_symbol)
    # The .info property will now use the TencentDataSource
    info = stock.info

    print(f"\n--- Info for {ticker_symbol} from Tencent ---")
    if info and info.get('symbol', '').lower() == ticker_symbol.lower():
        # Pretty print the info dictionary, ensuring Chinese characters are displayed correctly
        print(json.dumps(info, indent=4, ensure_ascii=False))
        print("\n--> Success! Data was fetched and adapted from the Tencent source.")
    else:
        print("Could not retrieve valid info.")
        print("Note: The Tencent API might be unstable or the ticker symbol format could be incorrect.")
        print(f"Received: {info}")

except Exception as e:
    print(f"\nAn error occurred: {e}")

print("\n--> Switching back to default 'yahoo' source")
yf.set_data_source('yahoo')
goog = yf.Ticker('GOOGL')
print("\n--> Fetching info for GOOGL using Yahoo source...")
info_yahoo = goog.info
print(f"Successfully fetched info for {info_yahoo.get('shortName')} from Yahoo.")
