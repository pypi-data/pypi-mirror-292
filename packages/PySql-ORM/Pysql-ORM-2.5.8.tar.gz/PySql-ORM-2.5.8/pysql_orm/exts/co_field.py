from datetime import datetime
from pyco_types import DateFmt, IntegerFmt
from pyco_types.const import CoEnumBase
from pyco_types._common import G_Symbol_UNSET, CommonException
from sqlalchemy.schema import CreateTable, Column

## @formatter:off
###; update@NICO: 202400807
###; @ZH:结构化DDL时按类型排序，可以对大数据有较好的优化查询效果
EX_IMPL_NAME_SCORE = {
    "int"           : 100000,
    "interger"      : 100000,
    "small_integer" : 110000,
    "boolean"       : 120000,
    "bit"           : 120000,
    "tinyint"       : 130000,
    "enum"          : 140000,
    "big_integer"   : 150000,
    "numeric"       : 190000,
    "float"         : 200000,
    "real"          : 240000,
    "date"          : 310000,
    "time"          : 320000,
    "datetime"      : 330000,
    "timestamp"     : 360000,
    "char"          : 400000,
    "varchar"       : 410000,
    "string"        : 430000,
    "text"          : 600000,
    "json"          : 700000,
    "array"         : 720000,
    "blob"          : 800000,
    "binary"        : 820000,
    "varbinary"     : 850000,
    "longtext"      : 910000,
    "longblob"      : 920000,
    "large_binary"  : 970000,
}

EX_PYTHON_TYPE_SCORE = {
    int     : 110000,
    bool    : 120000,
    str     : 440000,
    datetime: 340000,
    dict    : 750000,
}
## @formatter: on

def get_python_type(coltype, _is_silent=True):
    """
    @coltype: 
        - instance of sqlalchemy.sql.sqltypes.TypeEngine(>=v1.4.36)
        - instance of sqlalchemy.types.TypeDecorator  
    """
    try:
        impl = getattr(coltype, "impl", None)
        if impl is None:
            impl = coltype
    except Exception as e:
        impl = coltype
    try:
        pty = getattr(impl, "python_type", None)
        if isinstance(pty, property):
            return pty.fget(impl)
        else:
            return pty
    except Exception as e2:
        if _is_silent:
            return None
        raise e2


def get_impl_label(coltype, _is_silent=True):
    try:
        impl = getattr(coltype, "impl", None)
        if impl is None:
            impl = coltype
    except Exception as e:
        impl = coltype        
    label = str(getattr(impl, "__visit_name__", "")).lower()
    if label == "type_decorator":
        return str(coltype.__class__.__name__).lower()
    return label


class CoField(Column):
    inherit_cache = True  # 表明这个自定义构造支持缓存继承

    def __new__(cls, *args, **kwargs):
        pass

    def __init__(self, 
                 *args, alias=None, enum_cls=None, help_tips="",
                 _convert_func=None, _convert_kwargs=None,
                 _reshape_func=None, _reshape_kwargs=None,
                 **kwargs):
        super(CoField, self).__init__(*args, **kwargs)

        self.enum_cls = enum_cls
        self.python_type = get_python_type(self.type)
        
        self._convert_func = _convert_func
        self._convert_kwargs = _convert_kwargs or {}
        self._reshape_func = _reshape_func
        self._reshape_kwargs = _reshape_kwargs or {}
        
        self._co_field_alias = alias
        self._co_field_kwargs = kwargs
        self._co_field_type = None
        
        if len(args) > 0:
            self._co_field_type = args[0]

        self._co_impl_label = get_impl_label(self.type)
        if not isinstance(help_tips, list):
            if help_tips:
                help_tips = [str(help_tips)]
            else:
                help_tips = []

        if not self.comment:
            _is_type_deco = getattr(self._co_field_type,"_is_type_decorator", False
            ) 
            if _is_type_deco:
                self.comment = self._co_field_type.__class__.__name__
                help_tips.append(self.comment)
                
        elif isinstance(self.comment, type):
            if issubclass(self.comment, CoEnumBase):
                self.enum_cls = self.comment
                enum_title = f'"{self.comment.__name__}"'
                help_tips.append(enum_title)
                help_tips.extend(self.comment.list_options())
                self.comment = enum_title
        elif isinstance(self.comment, str):
            help_tips.append(str(self.comment))
        else:
            self.comment = str(self.comment)

        self.help_tips = help_tips
        
        ##; create order by asc
        # self._ori_creation_order = self._creation_order
        _creation_order = getattr(self, "_creation_order", 0)
        w = self._calucate_score()
        self._creation_order = _creation_order + w

    def _calucate_score(self, failsafe_score = 10 ** 7):
        if self.is_primary_key:
            return 0
        w = EX_IMPL_NAME_SCORE.get(self._co_impl_label, 0)
        if w <= 0:
            w = EX_PYTHON_TYPE_SCORE.get(self.python_type, failsafe_score)
        return w

    @property
    def is_primary_key(self):
        primary_key = self._co_field_kwargs.get("primary_key", False)
        return primary_key    # type: bool

    @property
    def is_index_key(self):
        is_index = self._co_field_kwargs.get("index", False)
        return is_index    # type: bool
