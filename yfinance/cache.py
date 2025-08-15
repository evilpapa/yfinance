import peewee as _peewee
from threading import Lock
import os as _os
import platformdirs as _ad
import atexit as _atexit
import datetime as _dt
import pickle as _pkl

from .utils import get_yf_logger

_cache_init_lock = Lock()


# --------------
# 时区缓存
# --------------

class _TzCacheException(Exception):
    """时区缓存自定义异常"""
    pass


class _TzCacheDummy:
    """如果时区缓存被禁用，则使用此虚拟缓存"""

    def lookup(self, tkr):
        return None

    def store(self, tkr, tz):
        pass

    @property
    def tz_db(self):
        return None


class _TzCacheManager:
    """时区缓存管理器"""
    _tz_cache = None

    @classmethod
    def get_tz_cache(cls):
        """获取时区缓存实例"""
        if cls._tz_cache is None:
            with _cache_init_lock:
                cls._initialise()
        return cls._tz_cache

    @classmethod
    def _initialise(cls, cache_dir=None):
        """初始化时区缓存"""
        cls._tz_cache = _TzCache()


class _TzDBManager:
    """时区数据库管理器"""
    _db = None
    _cache_dir = _os.path.join(_ad.user_cache_dir(), "py-yfinance")

    @classmethod
    def get_database(cls):
        """获取数据库实例"""
        if cls._db is None:
            cls._initialise()
        return cls._db

    @classmethod
    def close_db(cls):
        """关闭数据库连接"""
        if cls._db is not None:
            try:
                cls._db.close()
            except Exception:
                # 必须丢弃异常，因为Python正在退出
                pass


    @classmethod
    def _initialise(cls, cache_dir=None):
        """初始化数据库"""
        if cache_dir is not None:
            cls._cache_dir = cache_dir

        if not _os.path.isdir(cls._cache_dir):
            try:
                _os.makedirs(cls._cache_dir)
            except OSError as err:
                raise _TzCacheException(f"创建TzCache文件夹时出错: '{cls._cache_dir}' 原因: {err}")
        elif not (_os.access(cls._cache_dir, _os.R_OK) and _os.access(cls._cache_dir, _os.W_OK)):
            raise _TzCacheException(f"无法在TzCache文件夹中读写: '{cls._cache_dir}'")

        cls._db = _peewee.SqliteDatabase(
            _os.path.join(cls._cache_dir, 'tkr-tz.db'),
            pragmas={'journal_mode': 'wal', 'cache_size': -64}
        )

        old_cache_file_path = _os.path.join(cls._cache_dir, "tkr-tz.csv")
        if _os.path.isfile(old_cache_file_path):
            _os.remove(old_cache_file_path)

    @classmethod
    def set_location(cls, new_cache_dir):
        """设置缓存位置"""
        if cls._db is not None:
            cls._db.close()
            cls._db = None
        cls._cache_dir = new_cache_dir

    @classmethod
    def get_location(cls):
        """获取缓存位置"""
        return cls._cache_dir

# Python退出时关闭数据库
_atexit.register(_TzDBManager.close_db)


tz_db_proxy = _peewee.Proxy()
class _TZ_KV(_peewee.Model):
    """时区键值对模型"""
    key = _peewee.CharField(primary_key=True)
    value = _peewee.CharField(null=True)
    
    class Meta:
        database = tz_db_proxy
        without_rowid = True


class _TzCache:
    """时区缓存实现"""
    def __init__(self):
        self.initialised = -1
        self.db = None
        self.dummy = False

    def get_db(self):
        """获取数据库实例"""
        if self.db is not None:
            return self.db

        try:
            self.db = _TzDBManager.get_database()
        except _TzCacheException as err:
            get_yf_logger().info(f"创建TzCache失败，原因: {err}. "
                                 "将不使用TzCache。 "
                                 "提示: 您可以使用 'set_tz_cache_location(mylocation)' 将缓存定向到其他位置")
            self.dummy = True
            return None
        return self.db

    def initialise(self):
        """初始化缓存"""
        if self.initialised != -1:
            return

        db = self.get_db()
        if db is None:
            self.initialised = 0  # 失败
            return

        db.connect()
        tz_db_proxy.initialize(db)
        try:
            db.create_tables([_TZ_KV])
        except _peewee.OperationalError as e:
            if 'WITHOUT' in str(e):
                _TZ_KV._meta.without_rowid = False
                db.create_tables([_TZ_KV])
            else:
                raise
        self.initialised = 1  # 成功

    def lookup(self, key):
        """查找键对应的值"""
        if self.dummy:
            return None

        if self.initialised == -1:
            self.initialise()

        if self.initialised == 0:  # 失败
            return None

        try:
            return _TZ_KV.get(_TZ_KV.key == key).value
        except _TZ_KV.DoesNotExist:
            return None

    def store(self, key, value):
        """存储键值对"""
        if self.dummy:
            return

        if self.initialised == -1:
            self.initialise()

        if self.initialised == 0:  # 失败
            return

        db = self.get_db()
        if db is None:
            return
        try:
            if value is None:
                q = _TZ_KV.delete().where(_TZ_KV.key == key)
                q.execute()
                return
            with db.atomic():
                _TZ_KV.insert(key=key, value=value).execute()
        except _peewee.IntegrityError:
            # 完整性错误意味着键已存在。尝试更新键。
            old_value = self.lookup(key)
            if old_value != value:
                get_yf_logger().debug(f"键 {key} 的值从 {old_value} 更改为 {value}.")
                with db.atomic():
                    q = _TZ_KV.update(value=value).where(_TZ_KV.key == key)
                    q.execute()


def get_tz_cache():
    """获取时区缓存的公共函数"""
    return _TzCacheManager.get_tz_cache()



# --------------
# Cookie缓存
# --------------

class _CookieCacheException(Exception):
    """Cookie缓存自定义异常"""
    pass


class _CookieCacheDummy:
    """如果Cookie缓存被禁用，则使用此虚拟缓存"""

    def lookup(self, tkr):
        return None

    def store(self, tkr, Cookie):
        pass

    @property
    def Cookie_db(self):
        return None


class _CookieCacheManager:
    """Cookie缓存管理器"""
    _Cookie_cache = None

    @classmethod
    def get_cookie_cache(cls):
        """获取Cookie缓存实例"""
        if cls._Cookie_cache is None:
            with _cache_init_lock:
                cls._initialise()
        return cls._Cookie_cache

    @classmethod
    def _initialise(cls, cache_dir=None):
        """初始化Cookie缓存"""
        cls._Cookie_cache = _CookieCache()


class _CookieDBManager:
    """Cookie数据库管理器"""
    _db = None
    _cache_dir = _os.path.join(_ad.user_cache_dir(), "py-yfinance")

    @classmethod
    def get_database(cls):
        """获取数据库实例"""
        if cls._db is None:
            cls._initialise()
        return cls._db

    @classmethod
    def close_db(cls):
        """关闭数据库连接"""
        if cls._db is not None:
            try:
                cls._db.close()
            except Exception:
                # 必须丢弃异常，因为Python正在退出
                pass


    @classmethod
    def _initialise(cls, cache_dir=None):
        """初始化数据库"""
        if cache_dir is not None:
            cls._cache_dir = cache_dir

        if not _os.path.isdir(cls._cache_dir):
            try:
                _os.makedirs(cls._cache_dir)
            except OSError as err:
                raise _CookieCacheException(f"创建CookieCache文件夹时出错: '{cls._cache_dir}' 原因: {err}")
        elif not (_os.access(cls._cache_dir, _os.R_OK) and _os.access(cls._cache_dir, _os.W_OK)):
            raise _CookieCacheException(f"无法在CookieCache文件夹中读写: '{cls._cache_dir}'")

        cls._db = _peewee.SqliteDatabase(
            _os.path.join(cls._cache_dir, 'cookies.db'),
            pragmas={'journal_mode': 'wal', 'cache_size': -64}
        )

    @classmethod
    def set_location(cls, new_cache_dir):
        """设置缓存位置"""
        if cls._db is not None:
            cls._db.close()
            cls._db = None
        cls._cache_dir = new_cache_dir

    @classmethod
    def get_location(cls):
        """获取缓存位置"""
        return cls._cache_dir

# Python退出时关闭数据库
_atexit.register(_CookieDBManager.close_db)


Cookie_db_proxy = _peewee.Proxy()
class ISODateTimeField(_peewee.DateTimeField):
    """自定义日期时间字段，确保以ISO格式读写"""
    def db_value(self, value):
        if value and isinstance(value, _dt.datetime):
            return value.isoformat()
        return super().db_value(value)
    def python_value(self, value):
        if value and isinstance(value, str) and 'T' in value:
            return _dt.datetime.fromisoformat(value)
        return super().python_value(value)
class _CookieSchema(_peewee.Model):
    """Cookie数据库模式"""
    strategy = _peewee.CharField(primary_key=True)
    fetch_date = ISODateTimeField(default=_dt.datetime.now)
    
    cookie_bytes = _peewee.BlobField()

    class Meta:
        database = Cookie_db_proxy
        without_rowid = True


class _CookieCache:
    """Cookie缓存实现"""
    def __init__(self):
        self.initialised = -1
        self.db = None
        self.dummy = False

    def get_db(self):
        """获取数据库实例"""
        if self.db is not None:
            return self.db

        try:
            self.db = _CookieDBManager.get_database()
        except _CookieCacheException as err:
            get_yf_logger().info(f"创建CookieCache失败，原因: {err}. "
                                 "将不使用CookieCache。 "
                                 "提示: 您可以使用 'set_tz_cache_location(mylocation)' 将缓存定向到其他位置")
            self.dummy = True
            return None
        return self.db

    def initialise(self):
        """初始化缓存"""
        if self.initialised != -1:
            return

        db = self.get_db()
        if db is None:
            self.initialised = 0  # 失败
            return

        db.connect()
        Cookie_db_proxy.initialize(db)
        try:
            db.create_tables([_CookieSchema])
        except _peewee.OperationalError as e:
            if 'WITHOUT' in str(e):
                _CookieSchema._meta.without_rowid = False
                db.create_tables([_CookieSchema])
            else:
                raise
        self.initialised = 1  # 成功

    def lookup(self, strategy):
        """查找策略对应的Cookie"""
        if self.dummy:
            return None

        if self.initialised == -1:
            self.initialise()

        if self.initialised == 0:  # 失败
            return None

        try:
            data =  _CookieSchema.get(_CookieSchema.strategy == strategy)
            cookie = _pkl.loads(data.cookie_bytes)
            return {'cookie':cookie, 'age':_dt.datetime.now()-data.fetch_date}
        except _CookieSchema.DoesNotExist:
            return None

    def store(self, strategy, cookie):
        """存储策略对应的Cookie"""
        if self.dummy:
            return

        if self.initialised == -1:
            self.initialise()

        if self.initialised == 0:  # 失败
            return

        db = self.get_db()
        if db is None:
            return
        try:
            q = _CookieSchema.delete().where(_CookieSchema.strategy == strategy)
            q.execute()
            if cookie is None:
                return
            with db.atomic():
                cookie_pkl = _pkl.dumps(cookie, _pkl.HIGHEST_PROTOCOL)
                _CookieSchema.insert(strategy=strategy, cookie_bytes=cookie_pkl).execute()
        except _peewee.IntegrityError:
            raise

def get_cookie_cache():
    """获取Cookie缓存的公共函数"""
    return _CookieCacheManager.get_cookie_cache()



# --------------
# ISIN缓存
# --------------

class _ISINCacheException(Exception):
    """ISIN缓存自定义异常"""
    pass


class _ISINCacheDummy:
    """如果ISIN缓存被禁用，则使用此虚拟缓存"""

    def lookup(self, isin):
        return None

    def store(self, isin, tkr):
        pass

    @property
    def tz_db(self):
        return None


class _ISINCacheManager:
    """ISIN缓存管理器"""
    _isin_cache = None

    @classmethod
    def get_isin_cache(cls):
        """获取ISIN缓存实例"""
        if cls._isin_cache is None:
            with _cache_init_lock:
                cls._initialise()
        return cls._isin_cache

    @classmethod
    def _initialise(cls, cache_dir=None):
        """初始化ISIN缓存"""
        cls._isin_cache = _ISINCache()


class _ISINDBManager:
    """ISIN数据库管理器"""
    _db = None
    _cache_dir = _os.path.join(_ad.user_cache_dir(), "py-yfinance")

    @classmethod
    def get_database(cls):
        """获取数据库实例"""
        if cls._db is None:
            cls._initialise()
        return cls._db

    @classmethod
    def close_db(cls):
        """关闭数据库连接"""
        if cls._db is not None:
            try:
                cls._db.close()
            except Exception:
                # 必须丢弃异常，因为Python正在退出
                pass


    @classmethod
    def _initialise(cls, cache_dir=None):
        """初始化数据库"""
        if cache_dir is not None:
            cls._cache_dir = cache_dir

        if not _os.path.isdir(cls._cache_dir):
            try:
                _os.makedirs(cls._cache_dir)
            except OSError as err:
                raise _ISINCacheException(f"创建ISINCache文件夹时出错: '{cls._cache_dir}' 原因: {err}")
        elif not (_os.access(cls._cache_dir, _os.R_OK) and _os.access(cls._cache_dir, _os.W_OK)):
            raise _ISINCacheException(f"无法在ISINCache文件夹中读写: '{cls._cache_dir}'")

        cls._db = _peewee.SqliteDatabase(
            _os.path.join(cls._cache_dir, 'isin-tkr.db'),
            pragmas={'journal_mode': 'wal', 'cache_size': -64}
        )

    @classmethod
    def set_location(cls, new_cache_dir):
        """设置缓存位置"""
        if cls._db is not None:
            cls._db.close()
            cls._db = None
        cls._cache_dir = new_cache_dir

    @classmethod
    def get_location(cls):
        """获取缓存位置"""
        return cls._cache_dir

# Python退出时关闭数据库
_atexit.register(_ISINDBManager.close_db)


isin_db_proxy = _peewee.Proxy()
class _ISIN_KV(_peewee.Model):
    """ISIN键值对模型"""
    key = _peewee.CharField(primary_key=True)
    value = _peewee.CharField(null=True)
    created_at = _peewee.DateTimeField(default=_dt.datetime.now)
    
    class Meta:
        database = isin_db_proxy
        without_rowid = True


class _ISINCache:
    """ISIN缓存实现"""
    def __init__(self):
        self.initialised = -1
        self.db = None
        self.dummy = False

    def get_db(self):
        """获取数据库实例"""
        if self.db is not None:
            return self.db

        try:
            self.db = _ISINDBManager.get_database()
        except _ISINCacheException as err:
            get_yf_logger().info(f"创建ISINCache失败，原因: {err}. "
                                 "将不使用ISINCache。 "
                                 "提示: 您可以使用 'set_isin_cache_location(mylocation)' 将缓存定向到其他位置")
            self.dummy = True
            return None
        return self.db

    def initialise(self):
        """初始化缓存"""
        if self.initialised != -1:
            return

        db = self.get_db()
        if db is None:
            self.initialised = 0  # 失败
            return

        db.connect()
        isin_db_proxy.initialize(db)
        try:
            db.create_tables([_ISIN_KV])
        except _peewee.OperationalError as e:
            if 'WITHOUT' in str(e):
                _ISIN_KV._meta.without_rowid = False
                db.create_tables([_ISIN_KV])
            else:
                raise
        self.initialised = 1  # 成功

    def lookup(self, key):
        """查找键对应的值"""
        if self.dummy:
            return None

        if self.initialised == -1:
            self.initialise()

        if self.initialised == 0:  # 失败
            return None

        try:
            return _ISIN_KV.get(_ISIN_KV.key == key).value
        except _ISIN_KV.DoesNotExist:
            return None

    def store(self, key, value):
        """存储键值对"""
        if self.dummy:
            return

        if self.initialised == -1:
            self.initialise()

        if self.initialised == 0:  # 失败
            return

        db = self.get_db()
        if db is None:
            return
        try:
            if value is None:
                q = _ISIN_KV.delete().where(_ISIN_KV.key == key)
                q.execute()
                return

            # 删除超过一周的具有相同值的旧行
            one_week_ago = _dt.datetime.now() - _dt.timedelta(weeks=1)
            old_rows_query = _ISIN_KV.delete().where(
                (_ISIN_KV.value == value) & 
                (_ISIN_KV.created_at < one_week_ago)
            )
            old_rows_query.execute()

            with db.atomic():
                _ISIN_KV.insert(key=key, value=value).execute()

        except _peewee.IntegrityError:
            # 完整性错误意味着键已存在。尝试更新键。
            old_value = self.lookup(key)
            if old_value != value:
                get_yf_logger().debug(f"键 {key} 的值从 {old_value} 更改为 {value}.")
                with db.atomic():
                    q = _ISIN_KV.update(value=value, created_at=_dt.datetime.now()).where(_ISIN_KV.key == key)
                    q.execute()


def get_isin_cache():
    """获取ISIN缓存的公共函数"""
    return _ISINCacheManager.get_isin_cache()


# --------------
# 工具函数
# --------------

def set_cache_location(cache_dir: str):
    """
    设置创建 "py-yfinance" 缓存文件夹的路径。
    如果 "appdir.user_cache_dir()" 返回的默认文件夹不可写，则此函数很有用。
    必须在使用缓存之前调用（即在获取股票代码之前）。
    :param cache_dir: 用于缓存的路径
    :return: None
    """
    _TzDBManager.set_location(cache_dir)
    _CookieDBManager.set_location(cache_dir)
    _ISINDBManager.set_location(cache_dir)

def set_tz_cache_location(cache_dir: str):
    """set_cache_location的别名"""
    set_cache_location(cache_dir)
