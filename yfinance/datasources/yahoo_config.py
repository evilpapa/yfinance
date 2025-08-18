# This file contains the configuration for the Yahoo Finance data source.
# It is used by the GenericDataSource to fetch and parse data.

# The quoteSummary endpoint requires a list of modules.
_info_modules = [
    'financialData', 'quoteType', 'defaultKeyStatistics',
    'assetProfile', 'summaryDetail'
]
_info_modules_str = ",".join(_info_modules)

# The configuration dictionary.
# This structure is designed to be used by GenericDataSource.
yahoo_config = {
    "name": "YahooFinance",
    "endpoints": {
        # For methods that need to hit multiple endpoints, we use a list of configs.
        "info": [
            {
                "url": f"https://query2.finance.yahoo.com/v10/finance/quoteSummary/{{ticker}}?modules={_info_modules_str}",
                "data_path": "quoteSummary.result.0"
            },
            {
                "url": "https://query1.finance.yahoo.com/v7/finance/quote?symbols={ticker}",
                "data_path": "quoteResponse.result.0"
            }
        ]
    },
    "mappers": {
        # This section maps the desired yfinance field names (keys) to the
        # field names/paths found in the source's JSON response (values).
        "info": {
            # Fields from 'assetProfile' module
            'address1': 'assetProfile.address1',
            'city': 'assetProfile.city',
            'state': 'assetProfile.state',
            'zip': 'assetProfile.zip',
            'country': 'assetProfile.country',
            'phone': 'assetProfile.phone',
            'website': 'assetProfile.website',
            'industry': 'assetProfile.industry',
            'sector': 'assetProfile.sector',
            'longBusinessSummary': 'assetProfile.longBusinessSummary',
            'fullTimeEmployees': 'assetProfile.fullTimeEmployees',
            'companyOfficers': 'assetProfile.companyOfficers',

            # Fields from 'summaryDetail' module
            'previousClose': 'summaryDetail.previousClose.raw',
            'open': 'summaryDetail.open.raw',
            'dayLow': 'summaryDetail.dayLow.raw',
            'dayHigh': 'summaryDetail.dayHigh.raw',
            'regularMarketPreviousClose': 'summaryDetail.regularMarketPreviousClose.raw',
            'regularMarketOpen': 'summaryDetail.regularMarketOpen.raw',
            'regularMarketDayLow': 'summaryDetail.regularMarketDayLow.raw',
            'regularMarketDayHigh': 'summaryDetail.regularMarketDayHigh.raw',
            'dividendRate': 'summaryDetail.dividendRate.raw',
            'dividendYield': 'summaryDetail.dividendYield.raw',
            'exDividendDate': 'summaryDetail.exDividendDate.raw',
            'payoutRatio': 'summaryDetail.payoutRatio.raw',
            'fiveYearAvgDividendYield': 'summaryDetail.fiveYearAvgDividendYield.raw',
            'beta': 'summaryDetail.beta.raw',
            'trailingPE': 'summaryDetail.trailingPE.raw',
            'forwardPE': 'summaryDetail.forwardPE.raw',
            'volume': 'summaryDetail.volume.raw',
            'regularMarketVolume': 'summaryDetail.regularMarketVolume.raw',
            'averageVolume': 'summaryDetail.averageVolume.raw',
            'averageVolume10days': 'summaryDetail.averageVolume10days.raw',
            'averageDailyVolume10Day': 'summaryDetail.averageDailyVolume10Day.raw',
            'bid': 'summaryDetail.bid.raw',
            'ask': 'summaryDetail.ask.raw',
            'bidSize': 'summaryDetail.bidSize.raw',
            'askSize': 'summaryDetail.askSize.raw',
            'marketCap': 'summaryDetail.marketCap.raw',

            # Fields from 'defaultKeyStatistics' module
            'enterpriseValue': 'defaultKeyStatistics.enterpriseValue.raw',
            'forwardEps': 'defaultKeyStatistics.forwardEps.raw',
            'trailingEps': 'defaultKeyStatistics.trailingEps.raw',
            'bookValue': 'defaultKeyStatistics.bookValue.raw',
            'priceToBook': 'defaultKeyStatistics.priceToBook.raw',
            'enterpriseToRevenue': 'defaultKeyStatistics.enterpriseToRevenue.raw',
            'enterpriseToEbitda': 'defaultKeyStatistics.enterpriseToEbitda.raw',
            '52WeekChange': 'defaultKeyStatistics.52WeekChange.raw',
            'SandP52WeekChange': 'defaultKeyStatistics.SandP52WeekChange.raw',

            # Fields from 'financialData' module
            'currentPrice': 'financialData.currentPrice.raw',
            'targetHighPrice': 'financialData.targetHighPrice.raw',
            'targetLowPrice': 'financialData.targetLowPrice.raw',
            'targetMeanPrice': 'financialData.targetMeanPrice.raw',
            'targetMedianPrice': 'financialData.targetMedianPrice.raw',
            'recommendationMean': 'financialData.recommendationMean.raw',
            'recommendationKey': 'financialData.recommendationKey',
            'numberOfAnalystOpinions': 'financialData.numberOfAnalystOpinions.raw',
            'totalCash': 'financialData.totalCash.raw',
            'totalCashPerShare': 'financialData.totalCashPerShare.raw',
            'ebitda': 'financialData.ebitda.raw',
            'totalDebt': 'financialData.totalDebt.raw',
            'quickRatio': 'financialData.quickRatio.raw',
            'currentRatio': 'financialData.currentRatio.raw',
            'totalRevenue': 'financialData.totalRevenue.raw',
            'debtToEquity': 'financialData.debtToEquity.raw',
            'revenuePerShare': 'financialData.revenuePerShare.raw',
            'returnOnAssets': 'financialData.returnOnAssets.raw',
            'returnOnEquity': 'financialData.returnOnEquity.raw',
            'grossProfits': 'financialData.grossProfits.raw',
            'freeCashflow': 'financialData.freeCashflow.raw',
            'operatingCashflow': 'financialData.operatingCashflow.raw',
            'earningsGrowth': 'financialData.earningsGrowth.raw',
            'revenueGrowth': 'financialData.revenueGrowth.raw',
            'grossMargins': 'financialData.grossMargins.raw',
            'ebitdaMargins': 'financialData.ebitdaMargins.raw',
            'operatingMargins': 'financialData.operatingMargins.raw',

            # Fields from 'quoteType' module
            'symbol': 'quoteType.symbol',
            'quoteType': 'quoteType.quoteType',
            'shortName': 'quoteType.shortName',
            'longName': 'quoteType.longName',
            'exchange': 'quoteType.exchange',
            'timeZoneShortName': 'quoteType.timeZoneShortName',
            'timeZoneFullName': 'quoteType.timeZoneFullName',
            'market': 'quoteType.market',
        }
    }
}
