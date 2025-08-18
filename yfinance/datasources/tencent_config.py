# This file contains the configuration for the Tencent data source.

tencent_config = {
    "name": "Tencent",
    "endpoints": {
        "info": "http://qt.gtimg.cn/q={ticker}"
    }
    # Mappers are not needed here because the parsing and mapping logic
    # is handled by the specialized TencentDataSource class.
}
