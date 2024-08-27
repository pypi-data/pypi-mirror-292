import re
import warnings
import sqlalchemy as sa
from sqlalchemy import inspect
from sqlalchemy import orm
from sqlalchemy.orm.exc import UnmappedClassError
from sqlalchemy.schema import _get_table_key
from threading import Lock
from ._adapt import FsaAdaptError
from ._logger import logger
from ._langhelp import get_attr_of_package

try:
    # if sqlalchemy_version(">", "1.4"):
    from sqlalchemy.orm import (
        declarative_base,  # noqa
        DeclarativeMeta,
        declared_attr,
    )
except Exception as e:
    # SQLAlchemy <= 1.3
    try:
        from sqlalchemy.ext.declarative import (
        declarative_base,  # noqa
        DeclarativeMeta,
        declared_attr,
    )
    except Exception as e:
        logger.warning(e)
        logger.warning("[FSA]: retry with get_attr_of_package")
        declarative_base = get_attr_of_package("declarative_base", sa)
        DeclarativeMeta  = get_attr_of_package("declarative_base", sa)
        declared_attr  = get_attr_of_package("declarative_base", sa)
        


def should_set_tablename(cls):
    """Determine whether ``__tablename__`` should be automatically generated
    for a model.

    * If no class in the MRO sets a name, one should be generated.
    * If a declared attr is found, it should be used instead.
    * If a name is found, it should be used if the class is a mixin, otherwise
      one should be generated.
    * Abstract models should not have one generated.

    Later, :meth:`._BoundDeclarativeMeta.__table_cls__` will determine if the
    model looks like single or joined-table inheritance. If no primary key is
    found, the name will be unset.
    """
    if (
        cls.__dict__.get('__abstract__', False)
        or not any(isinstance(b, DeclarativeMeta) for b in cls.__mro__[1:])
    ):
        return False

    for base in cls.__mro__:
        if '__tablename__' not in base.__dict__:
            continue

        if isinstance(base.__dict__['__tablename__'], declared_attr):
            return False

        return not (
            base is cls
            or base.__dict__.get('__abstract__', False)
            or not isinstance(base, DeclarativeMeta)
        )

    return True


camelcase_re = re.compile(r'([A-Z]+)(?=[a-z0-9])')


def camel_to_snake_case(name):
    def _join(match):
        word = match.group()

        if len(word) > 1:
            return ('_%s_%s' % (word[:-1], word[-1])).lower()

        return '_' + word.lower()

    return camelcase_re.sub(_join, name).lstrip('_')


class NameMetaMixin(type):
    def __init__(cls, name, bases, d):
        if should_set_tablename(cls):
            cls.__tablename__ = camel_to_snake_case(cls.__name__)

        super(NameMetaMixin, cls).__init__(name, bases, d)

        # __table_cls__ has run at this point
        # if no table was created, use the parent table
        if (
            '__tablename__' not in cls.__dict__
            and '__table__' in cls.__dict__
            and cls.__dict__['__table__'] is None
        ):
            del cls.__table__

    def __table_cls__(cls, *args, **kwargs):
        """This is called by SQLAlchemy during mapper setup. It determines the
        final table object that the model will use.

        If no primary key is found, that indicates single-table inheritance,
        so no table will be created and ``__tablename__`` will be unset.
        """
        # check if a table with this name already exists
        # allows reflected tables to be applied to model by name
        key = _get_table_key(args[0], kwargs.get('schema'))

        if key in cls.metadata.tables:
            return sa.Table(*args, **kwargs)

        # if a primary key or constraint is found, create a table for
        # joined-table inheritance
        for arg in args:
            if (
                (isinstance(arg, sa.Column) and arg.primary_key)
                or isinstance(arg, sa.PrimaryKeyConstraint)
            ):
                return sa.Table(*args, **kwargs)

        # if no base classes define a table, return one
        # ensures the correct error shows up when missing a primary key
        for base in cls.__mro__[1:-1]:
            if '__table__' in base.__dict__:
                break
        else:
            return sa.Table(*args, **kwargs)

        # single-table inheritance, use the parent tablename
        if '__tablename__' in cls.__dict__:
            del cls.__tablename__


class BindMetaMixin(type):
    def __init__(cls, name, bases, d):
        bind_key = (
            d.pop('__bind_key__', None)
            or getattr(cls, '__bind_key__', None)
        )

        super(BindMetaMixin, cls).__init__(name, bases, d)

        if bind_key is not None and getattr(cls, '__table__', None) is not None:
            cls.__table__.info['bind_key'] = bind_key


class DefaultMeta(NameMetaMixin, BindMetaMixin, DeclarativeMeta):
    pass


class _ClassProperty:
    def __init__(self, fget=None):
        self.fget = fget
        self.fset = None
        self.fdel = None

    def setter(self, fset):
        self.fset = fset
        return self

    def __get__(self, instance, owner):
        if self.fget is None:
            raise AttributeError("getter not defined")
        return self.fget(owner)


class Model(object):
    """Base class for SQLAlchemy declarative base model.

    To define models, subclass :attr:`db.Model <SQLAlchemy.Model>`, not this
    class. To customize ``db.Model``, subclass this and pass it as
    ``model_class`` to :class:`SQLAlchemy`.
    """

    #: Query class used by :attr:`query`. Defaults to
    # :class:`SQLAlchemy.Query`, which defaults to :class:`BaseQuery`.
    query_class = None

    #: Convenience property to query the database for instances of this model
    # using the current session. Equivalent to ``db.session.query(Model)``
    # unless :attr:`query_class` has been changed.
    query = None

    _fsa = None
    _fsa_lock = None
    _fsa_session = None

    def __repr__(self):
        identity = inspect(self).identity
        if identity is None:
            pk = "(transient {0})".format(id(self))
        else:
            pk = ', '.join(map(str, identity))
        return '<{0} {1}>'.format(type(self).__name__, pk)

    @_ClassProperty
    def fsa_session(cls):
        if cls._fsa_session is not None:
            return cls._fsa_session
        if cls._fsa is not None:
            return cls._fsa.session
        raise FsaAdaptError(f"{cls}._fsa is not set, it should be a instance of <FSA_Interface>")

    @fsa_session.setter
    def fsa_session(cls, value):
        if isinstance(value, FSA_Interface):
            cls._fsa = value
        elif isinstance(value, orm.Session):
            cls._fsa_session = value

    @classmethod
    def fsa_lock(cls):
        if cls._fsa_lock is None:
            cls._fsa_lock = Lock()
        return cls._fsa_lock


class _QueryProperty(object):
    def __init__(self, fsa):
        self.sa = fsa
        self._fsa = fsa

    def __get__(self, obj, type):
        try:
            mapper = orm.class_mapper(type)
            if mapper:
                return type.query_class(mapper, session=self._fsa.session())
        except UnmappedClassError:
            return None


class FSA_Interface(object):
    _ModelDecl = None
    _ModelClass = Model
    _QueryClass = orm.Query
    _app_framework = ""

    @property
    def Query(self):
        return self._QueryClass

    @property
    def Model(self):
        if self._ModelDecl is None:
            self._ModelDecl = self.make_declarative_base(self._ModelClass, None)
        return self._ModelDecl

    @Model.setter
    def Model(self, val):
        self._ModelClass = val

    @property
    def engine(self):
        raise NotImplementedError()

    @property
    def session(self):
        raise NotImplementedError()

    @property
    def metadata(self):
        raise NotImplementedError()

    def init_app(self):
        raise NotImplementedError()

    def get_app(self, nullable=True, **kwargs):
        raise NotImplementedError()

    def make_declarative_base(self, model: type, metadata=None):
        """Creates the declarative base that all models will inherit from.

        :param model: base model class (or a tuple of base classes) to pass
            to :func:`~sqlalchemy.ext.declarative.declarative_base`. Or a class
            returned from ``declarative_base``, in which case a new base class
            is not created.
        :param metadata: :class:`~sqlalchemy.MetaData` instance to use, or
            none to use SQLAlchemy's default.

        .. versionchanged 2.3.0::
            ``model`` can be an existing declarative base in order to support
            complex customization such as changing the metaclass.
        """
        if not isinstance(model, DeclarativeMeta):
            model = declarative_base(
                cls=model,
                name='Model',
                metadata=metadata,
                metaclass=DefaultMeta
            )

        # if user passed in a declarative base and a metaclass for some reason,
        # make sure the base uses the metaclass
        if metadata is not None and model.metadata is not metadata:
            model.metadata = metadata

        if not getattr(model, 'query_class', None):
            model.query_class = self.Query

        model.query = _QueryProperty(self)
        model.sa = self
        model._fsa = self
        return model
