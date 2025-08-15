class YFException(Exception):
    """yfinance库的基类异常。"""
    def __init__(self, description=""):
        super().__init__(description)


class YFDataException(YFException):
    """与数据相关的异常。"""
    pass


class YFNotImplementedError(NotImplementedError):
    """当从Yahoo API获取的方法未实现时引发。"""
    def __init__(self, method_name):
        super().__init__(f"尚未实现从Yahoo API获取'{method_name}'")


class YFTickerMissingError(YFException):
    """当股票代码可能已退市时引发。"""
    def __init__(self, ticker, rationale):
        super().__init__(f"${ticker}: 可能已退市; {rationale}")
        self.rationale = rationale
        self.ticker = ticker


class YFTzMissingError(YFTickerMissingError):
    """当找不到时区时引发。"""
    def __init__(self, ticker):
        super().__init__(ticker, "找不到时区")


class YFPricesMissingError(YFTickerMissingError):
    """当找不到价格数据时引发。"""
    def __init__(self, ticker, debug_info):
        self.debug_info = debug_info
        if debug_info != '':
            super().__init__(ticker, f"找不到价格数据 {debug_info}")
        else:
            super().__init__(ticker, "找不到价格数据")


class YFEarningsDateMissing(YFTickerMissingError):
    """当找不到财报日期时引发。"""
    # 注意：此异常当前未被引发。添加以备将来使用。
    def __init__(self, ticker):
        super().__init__(ticker, "找不到财报日期")


class YFInvalidPeriodError(YFException):
    """当提供了无效的时间段时引发。"""
    def __init__(self, ticker, invalid_period, valid_ranges):
        self.ticker = ticker
        self.invalid_period = invalid_period
        self.valid_ranges = valid_ranges
        super().__init__(f"{self.ticker}: 时间段 '{invalid_period}' 无效, "
                         f"必须是以下之一: {valid_ranges}")


class YFRateLimitError(YFException):
    """当请求被速率限制时引发。"""
    def __init__(self):
        super().__init__("请求过多。已速率限制。请稍后再试。")
