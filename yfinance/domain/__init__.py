# domain/__init__.py

# 从本地模块导入Sector和Industry类
from .sector import Sector
from .industry import Industry

# 定义__all__列表，指定通过 'from yfinance.domain import *' 导入的模块
__all__ = ['Sector', 'Industry']
