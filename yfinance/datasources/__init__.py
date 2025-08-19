from .factory import DataSourceFactory
from .yahoo import YahooDataSource
from .akshare import AkshareDataSource

# 注册所有可用的数据源类
# Register all available data source classes
DataSourceFactory.register_source("yahoo", YahooDataSource)
DataSourceFactory.register_source("akshare", AkshareDataSource)
