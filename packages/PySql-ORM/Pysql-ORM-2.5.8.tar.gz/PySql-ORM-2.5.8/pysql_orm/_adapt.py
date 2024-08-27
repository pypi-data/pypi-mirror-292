import os
import types
import warnings

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.engine.url import make_url, URL
from pyco_types._common import G_Symbol_UNSET


class FSADeprecationWarning(DeprecationWarning):
    pass


warnings.simplefilter('always', FSADeprecationWarning)


class FsaAdaptError(SQLAlchemyError):
    code = 50500

    def __init__(self, msg="", errno=50500, **kwargs):
        self.msg = msg
        self.errno = errno
        self._ext_kwargs = kwargs

    def _code_str(self):
        return f"<FsaAdaptError:{self.errno}> {self.msg}"

    def __getattr__(self, item):
        return self._ext_kwargs.get(item, G_Symbol_UNSET)

    def __str__(self):
        if self._ext_kwargs:
            return f"{self._code_str()} ({self._ext_kwargs})"
        else:
            return self._code_str()


class AdaptorMeta(type):
    """usage sample:
    class A(metaclass=AdaptorMeta)
    
    """

    def __call__(cls, *args, **kwargs):
        mtp = super()
        # ms = cls.mro()
        if cls is not AppCfgAdaptor:
            obj = mtp.__call__(*args, **kwargs)
            AppCfgAdaptor.__init__(obj, *args, **kwargs)
            cls.__init__(obj, *args, **kwargs)
        else:
            obj = AppCfgAdaptor.__new__(cls, *args, **kwargs)
        return obj


# class AppCfgAdaptor(metaclass=_AdaptorMeta):
class AppCfgAdaptor():
    _extend_attrs = {}
    _refered_cfg = {}
    _app_config = None
    _app = None

    ALIAS_CONFIG_KEYS = ["_app_config", "app_config", "config"]

    def __new__(
        cls, *args,
        _enable_extend_attrs=True, _enable_extend_kwargs=True,
        **kwargs
    ):
        self = super().__new__(cls)
        self._app = None
        self._app_config = {}
        self._is_synced = False

        self._ext_args = args
        self._ext_kwargs = kwargs
        self._enable_extend_attrs = _enable_extend_attrs
        self._enable_extend_kwargs = _enable_extend_kwargs
        self._refered_cfg = {}
        return self

    def __init__(self, *args, **kwargs):
        self._ext_args = args
        self._ext_kwargs = kwargs
        self._app = None
        self._app_config = {}
        self._is_synced = False
        self._refered_cfg = {}


    def __getattr__(self, item):
        if self._enable_extend_attrs and self._extend_attrs:
            val = self._extend_attrs.get(item, G_Symbol_UNSET)
            if val is not G_Symbol_UNSET:
                return val

        if self._enable_extend_kwargs and self._ext_kwargs:
            val = self._ext_kwargs.get(item, G_Symbol_UNSET)
            if val is not G_Symbol_UNSET:
                return val
        raise AttributeError(f"AttributeError: failed to get ${item} of {self}")

    def __str__(self):
        return f"<AppCfgAdaptor: {self.__class__.__name__}>" \
               f"{self._ext_args},{self._ext_kwargs}"

    def __repr__(self):
        if self.app_config:
            return f"<{self.__class__.__name__}(app={str(self._app)}, app_config={type(self.app_config)})> "
        else:
            return f"<{self.__class__.__name__}(app={str(self._app)}, app_config={self.app_config})>"

    def get_app(self, nullable=True, **kwargs):
        if self._app:
            return self._app
        return self._ext_kwargs.get("app", None)

    @property
    def app_config(self):
        # return type: dict 
        if self._is_synced and self._app_config:
            return self._app_config
        app = self.get_app(nullable=True)
        if app is not None:
            cfg = getattr(app, "config", {})
            if cfg is self._app_config:
                self._is_synced = True
            elif cfg and isinstance(cfg, dict):
                if self._app_config:
                    cfg.update(self._app_config)
                self._app_config = cfg
                self._is_synced = True
            else:
                self._is_synced = False
        return self._app_config

    @app_config.setter
    def app_config(self, value: dict):
        if value is None:
            self._app_config = {}
            warnings.warn(
                f'{self}: self._app_config must be A Dict, '
                f'but recv "self.app_config(None)",'
                f'failsafe to set defaults to {{}}',
            )
        else:
            if not isinstance(value, dict):
                warnings.warn(
                    f'{self}: self._app_config must be A Dict, '
                    f'but recv "self.app_config(value:{type(value)})",'
                    f'it would raise error if use self.cfg_opotion, '
                    f'suggest to use `flask.config.Config` to convert it.'
                )
            self._app_config = value

    def update_config(self, **kwargs):
        self._app_config.update(kwargs)


# class FsaAppAdaptor(AppCfgAdaptor, metaclass=_AdaptorMeta):
class FsaAppAdaptor(AppCfgAdaptor):
    _refered_cfg = {}
    _app_config = None
    _app = None

    ALIAS_CONFIG_KEYS = ["_app_config", "app_config", "config"]

    def __str__(self):
        return f"<FsaAppAdaptor: {self.__class__.__name__}>"

    def __repr__(self):
        if self._app_config:
            return f"<{self.__class__.__name__}(app={str(self._app)}, app_config={type(self.app_config)})> "
        else:
            return f"<{self.__class__.__name__}(app={str(self._app)}, app_config={self.app_config})>"

    def check_debug(self):
        if os.environ.get("DEBUG"):
            return True
        if not isinstance(self.app_config, dict):
            return True
        if self.app_config.get("DEBUG", False):
            return True
        rq = self.app_config.get('SQLALCHEMY_RECORD_QUERIES', None)
        if rq is not None:
            return bool(rq)
        return self.app_config.get('TESTING', False)

    def cfg_option(
        self, key, default_value=None, nullable=True,
        decode_func=None, alias_keys=None, **kwargs
    ):
        val = self.app_config.get(key, None)
        if val is None:
            if alias_keys and isinstance(alias_keys, (list, tuple)):
                for ak in alias_keys:
                    val = self.app_config.get(ak, None)
                    if val is not None:
                        if self.check_debug():
                            warnings.warn(f'{self}: unset config[{key}], alias({ak}={val})')
                        break

            if val is None:
                val = default_value
                if self.check_debug():
                    warnings.warn(f'{self}: unset config[{key}], default_value="{default_value}"')

            if not nullable and default_value is None:
                raise FsaAdaptError(
                    msg=f'{self}: config[{key}] is required!',
                    errno=50520
                )

        elif callable(decode_func):
            val = decode_func(val)

        self._refered_cfg[key] = val
        return val

    def get_uri(self, default_value="", nullable=True, safety_wrap=False, **kwargs):
        m = self.cfg_option('SQLALCHEMY_DATABASE_URI', default_value, nullable=nullable, **kwargs)
        if safety_wrap and isinstance(m, str):
            m = m.split("@", 1)[-1]
        return m
    
    def fetch_bind_keys(self):
        res = self._refered_cfg.get("all_bind_keys", [])
        if res:
            return res
        res = [None]
        binds = self.cfg_option('SQLALCHEMY_BINDS', default_value={})
        if isinstance(binds, dict):
            res.extend(binds.keys())
        elif isinstance(binds, (tuple, list)):
            res.extend(binds)
        self._refered_cfg["all_bind_keys"] = res
        return res

    @classmethod
    def make_config(cls, cfg: dict):
        ##; @SQLALCHEMY_DATABASE_URI:
        ###; "mysql+mysqldb://{user}:{passwd}@{host}:{port}/{db_name}?charset=utf8mb4"  
        ###; "sqlite:///{local_db_file}"
        cfg.setdefault('SQLALCHEMY_DATABASE_URI', 'sqlite:///:memory:')
        cfg.setdefault('SQLALCHEMY_BINDS', None)
        cfg.setdefault('SQLALCHEMY_NATIVE_UNICODE', None)
        cfg.setdefault('SQLALCHEMY_ECHO', False)
        cfg.setdefault('SQLALCHEMY_RECORD_QUERIES', None)
        cfg.setdefault('SQLALCHEMY_POOL_SIZE', None)
        cfg.setdefault('SQLALCHEMY_POOL_TIMEOUT', None)
        cfg.setdefault('SQLALCHEMY_POOL_RECYCLE', None)
        cfg.setdefault('SQLALCHEMY_MAX_OVERFLOW', None)
        cfg.setdefault('SQLALCHEMY_COMMIT_ON_TEARDOWN', False)
        cfg.setdefault('SQLALCHEMY_TRACK_MODIFICATIONS', False)
        cfg.setdefault('SQLALCHEMY_ENGINE_OPTIONS', {})
        return cfg

    

    def apply_pool_defaults(self, app=None, options=None):
        """
        .. versionchanged:: 2.5
            Returns the ``options`` dict, for consistency with
            :meth:`apply_driver_hacks`.
        """
        if options is None:
            options = {}

        if app is None:
            def _setdefault(optionkey, configkey):
                value = self.cfg_option(configkey)
                if value is not None:
                    options[optionkey] = value
        else:
            app_cfg = getattr(app, "config", {})

            def _setdefault(optionkey, configkey):
                value = self.cfg_option(configkey)
                if value is not None:
                    options[optionkey] = value
                else:
                    value = app_cfg.get(configkey)
                    if value is not None:
                        options[optionkey] = value

        _setdefault('pool_size', 'SQLALCHEMY_POOL_SIZE')
        _setdefault('pool_timeout', 'SQLALCHEMY_POOL_TIMEOUT')
        _setdefault('pool_recycle', 'SQLALCHEMY_POOL_RECYCLE')
        _setdefault('max_overflow', 'SQLALCHEMY_MAX_OVERFLOW')
        return options

    def apply_driver_hacks(self, app, sa_url: URL, options: dict):
        """This method is called before engine creation and used to inject
        driver specific hacks into the options.  The `options` parameter is
        a dictionary of keyword arguments that will then be used to call
        the :func:`sqlalchemy.create_engine` function.

        The default implementation provides some saner defaults for things
        like pool sizes for MySQL and sqlite.  Also it injects the setting of
        `SQLALCHEMY_NATIVE_UNICODE`.

        .. versionchanged:: 2.5
            Returns ``(sa_url, options)``. SQLAlchemy 1.4 made the URL
            immutable, so any changes to it must now be passed back up
            to the original caller.
        """
        if isinstance(sa_url, str):
            sa_url = make_url(sa_url)
        elif not isinstance(sa_url, URL):
            raise FsaAdaptError(f"invalid sa_url={sa_url}")

        if sa_url.drivername.startswith('mysql'):
            charset = self.cfg_option("SQLALCHEMY_CHARSET", default_value="utf8mb4")
            charset = sa_url.query.setdefault("charset", charset)
            self._refered_cfg["SQLALCHEMY_CHARSET"] = charset

            if sa_url.drivername != 'mysql+gaerdbms':
                options.setdefault('pool_size', 10)
                options.setdefault('pool_recycle', 7200)

            ##; use_native_unicode only works for mysql
            ##;@ZH: @SQLALCHEMY_NATIVE_UNICODE: 指定是否使用数据库的本地 Unicode 支持。
            ##;@ZH: 当 use_native_unicode=True ，尽量用数据库原生的 Unicode 支持，而非 Python 的 Unicode 处理。
            ##;@ZH: 这样可以更好地与数据库本身的特性进行集成，提高性能并减少数据转换的开销。
            unu = self.cfg_option('SQLALCHEMY_NATIVE_UNICODE', default_value=True)
            if not unu:
                options['use_native_unicode'] = False
            else:
                options['use_native_unicode'] = True

            if self.check_debug() and unu is None:
                warnings.warn(
                    "The 'SQLALCHEMY_NATIVE_UNICODE' config option is deprecated and will be removed in"
                    " v3.0.  Use 'SQLALCHEMY_ENGINE_OPTIONS' instead.",
                    FSADeprecationWarning
                )

        elif sa_url.drivername == 'sqlite':
            pool_size = options.get('pool_size')
            detected_in_memory = False
            if sa_url.database in (None, '', ':memory:'):
                detected_in_memory = True
                from sqlalchemy.pool import StaticPool
                options['poolclass'] = StaticPool
                if 'connect_args' not in options:
                    options['connect_args'] = {}
                options['connect_args']['check_same_thread'] = False

                ##; we go to memory and the pool size was explicitly set
                ##; to 0 which is fail.  Let the user know that
                if pool_size == 0:
                    raise RuntimeError(
                        'SQLite in memory database with an '
                        'empty queue not possible due to data '
                        'loss.'
                    )
            ##; if pool size is None or explicitly set to 0 we assume the
            ##; user did not want a queue for this sqlite connection and
            ##; hook in the null pool.
            elif not pool_size:
                from sqlalchemy.pool import NullPool
                options['poolclass'] = NullPool

            ##; if it's not an in memory database we make the path absolute.
            if not detected_in_memory:
                root_path = getattr(app, "root_path", os.getcwd())
                fp_sqlite = os.path.join(root_path, sa_url.database)
                # sa_url.database = os.path.abspath(fp_sqlite)
                # sa_url.update_query_dict()
                # sa_url = sa_help._sa_url_set(
                #     sa_url, database=os.path.abspath(fp_sqlite)
                # )

        return sa_url, options
