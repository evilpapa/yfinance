from .factory import DataSourceFactory
from .yahoo_config import yahoo_config
from .tencent_config import tencent_config

# Automatically register the available sources when the package is imported.
DataSourceFactory.register_source("yahoo", yahoo_config)
DataSourceFactory.register_source("tencent", tencent_config)
