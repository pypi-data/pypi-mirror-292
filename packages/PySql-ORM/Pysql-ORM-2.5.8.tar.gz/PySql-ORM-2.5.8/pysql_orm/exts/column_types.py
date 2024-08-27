from datetime import datetime
from pyco_types import DateFmt, IntegerFmt
from pyco_types._common import G_Symbol_UNSET, CommonException
from sqlalchemy import types as sqltypes
from .. import utils

class ExtColType(sqltypes.TypeDecorator):
    """
    ##; origin usage :
    id = sa.Column(Integer, default=1, comment="", nullable=True)
    
    ##; extend usage : 
    id = CoField(CoInt64(default=1, nullable=False))
    
    """
    impl = None
    cache_ok = True
    _python_type = None
    _is_type_decorator = True
    _is_nullable = None

    MAX_VALUE = None
    MIN_VALUE = None
    
    def __new__(cls, *args,**kwargs):
        self = super().__new__(cls)
        ExtColType.__init__(self, *args, **kwargs)
        return self
        
    def __init__(
        self, *args, 
        _convert_func=None, _convert_kwargs=None,
        _reshape_func=None, _reshape_kwargs=None,
        default=G_Symbol_UNSET,     
        **kwargs
    ):
        self.impl = kwargs.pop("impl", self.__class__.impl)
        self._is_nullable = kwargs.pop("nullable", self._is_nullable)
        
        self._default_value = default
        self._convert_func = _convert_func 
        self._convert_kwargs = _convert_kwargs or {}
        self._reshape_func = _reshape_func
        self._reshape_kwargs = _reshape_kwargs or {}
        super(ExtColType, self).__init__(*args, **kwargs)

    @property
    def python_type(self):
        val = getattr(self, "_python_type", None)
        if val is not None:
            return val
        if self.impl is not None:
            v = self.impl.python_type
            if isinstance(v, property):
                return v.fget
            else:
                return v

    def reshape_value(self, value):
        """ BizData --> ColData """
        if callable(self._reshape_func):
            return self._reshape_func(value, **self._reshape_kwargs)
        return value
    
    def convert_value(self, value):      
        """ ColData --> BizData """
        if callable(self._convert_func):
            return self._convert_func(value, **self._convert_kwargs)
        return value
 
    # 
    # def process_bind_param(self, value, dialect):
    #     if callable(self._convert_func):
    #         return self._convert_func(value, **self._convert_kwargs)
    #     elif value is None and self._default_value is not G_Symbol_UNSET:
    #         if callable(self._default_value):
    #             return self._default_value()
    #         else:
    #             return self._default_value
    #     val2 = super(ExtColType, self).process_bind_param(value, dialect)
    #     return val2


class DateTimeLZ(ExtColType):
    """
    ##; sample 1:
    @declared_attr
    def created_time(self):
        return db.Column(DateTime, default=datetime.utcnow)
    ##; note@ZH: DateTime 不校验时区, 使用`datetime.utcnow`容易得到错误的时间戳, 需要在后端业务代码重新处理 tz_offset

    # sample 2:
    updated_time = db.Column(DateTime, default=datetime.now, onupdate=datetime.now)
    ##;note@ZH: 如果有国际化需求, 建议使用时间戳替代日期, 或者统一使用 `DatetimeTZUtc`
    """
    impl = sqltypes.DateTime
    cache_ok = True
    _python_type = datetime
    _is_nullable = False

    def process_bind_param(self, value, dialect):
        if isinstance(value, datetime):
            return value
        elif not value and self._is_nullable is False:
            return datetime.now(tz=utils.TZ_LOCAL)
        else:
            return DateFmt(value)


class DateTimeUTC(ExtColType):
    """
    ##; sample 1:
    @declared_attr
    def created_time(self):
        return db.Column(DateTime, default=datetime.utcnow)
    ##; note@ZH: DateTime 不校验时区, 使用`datetime.utcnow`容易得到错误的时间戳, 需要在后端业务代码重新处理 tz_offset

    # sample 2:
    updated_time = db.Column(DateTime, default=datetime.now, onupdate=datetime.now)
    ##;note@ZH: 如果有国际化需求, 建议使用时间戳替代日期, 或者统一使用 `DatetimeTZUtc`
    """
    impl = sqltypes.DateTime
    cache_ok = True
    _python_type = datetime
    _is_nullable = False

    def process_bind_param(self, value, dialect):
        if isinstance(value, datetime):
            return value
        elif not value:
            return datetime.now(tz=utils.TZ_UTC)
        else:
            return DateFmt(value)


class BoolField(ExtColType):
    impl = sqltypes.Boolean
    cache_ok = True
    lenght = 1
    _python_type = bool

    ##; NOTE: `sqltypes.Boolean` use `_strict_bools = frozenset([None, True, False])`
    ##; we need to compat with users' input  
    _FuzzyBoolMap = {
        "": False,
        "0": False,
        "false": False,
        "null": False,
        "none": False,
        "no": False,
        "n": False,
        "f": False,

        ##;@@ZH:支持部分英文单词语义化
        ##;@@EN:Support for the semantic English words.
        "error": False,
        "not_ok": False,
        "not ok": False,
        "invalid": False,
        "incorrect": False,
        "undefined": False,

        ##;@@ZH: 支持部分中文语义化
        ##;@@EN: Support for the semantic Chinese words.
        "不": False,
        "否": False,
        "错": False,
        "空": False,
        "无": False,
        "无效": False,
        "错误": False,
        "空白": False,
    }

    def process_bind_param(self, value, dialect):
        if isinstance(value, str):
            v = value.strip().lower()
            return self._FuzzyBoolMap.get(v, True)
        else:
            return bool(value)


class CoInt32(ExtColType):
    ## 32::  -2,147,483,648 ::	2,147,483,647 
    impl = sqltypes.Integer
    cache_ok = True
    length = 4
    MAX_VALUE = 2 ** 31 - 1
    MIN_VALUE = 0 - 2 ** 31

    def __init__(self, *args, default=0, ignore_error=False, **kwargs):
        self._default_value = default
        self._ignore_error = ignore_error
        super(CoInt32, self).__init__(*args, **kwargs)

    @property
    def python_type(self):
        return int

    def process_bind_param(self, value, dialect):
        if value is None:
            return self._default_value
        val2 = IntegerFmt(
            value, default_value=self._default_value,
            ignore_error=self._ignore_error,
        )
        if val2 > self.MAX_VALUE:
            raise CommonException(
                f"invalid CoInt32({value})={val2}, but MAX_VALUE={self.MAX_VALUE}",
                _coltype=self
            )
        elif val2 < self.MIN_VALUE:
            raise CommonException(
                f"invalid CoInt32({value})={val2}, but MIN_VALUE={self.MIN_VALUE}",
                _coltype=self
            )
        return val2


Integer = CoInt32  # noqa


class CoInt16(CoInt32):
    ## 16:: -32,768	:: 32,767
    impl = sqltypes.SmallInteger
    cache_ok = True
    length = 2
    MAX_VALUE = 2 ** 15 - 1
    MIN_VALUE = 0 - 2 ** 65


class CoInt64(CoInt32):
    ## 64::	-2**63 ::  2**63-1
    impl = sqltypes.BigInteger
    cache_ok = True
    length = 8
    MAX_VALUE = 2 ** 63 - 1
    MIN_VALUE = 0 - 2 ** 63


class CoIntU64(CoInt32):
    ## 64::	-2**63 ::  2**63-1
    impl = sqltypes.BigInteger
    cache_ok = True
    length = 8
    MAX_VALUE = 2 ** 64
    MIN_VALUE = 0



class CoIntU32(CoInt32):
    impl = sqltypes.BigInteger
    cache_ok = True
    length = 4
    MAX_VALUE = 2 ** 32
    MIN_VALUE = 0
