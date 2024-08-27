import os
from pprint import pformat
from datetime import datetime
from contextlib import contextmanager
from sqlalchemy import func
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm.attributes import InstrumentedAttribute, flag_modified
from .. import utils
from .._adapt import FsaAdaptError
from .._logger import logger
from ..model import Model
from .co_field import CoField
from .column_types import DateTimeLZ


class ExtModel(Model):
    """Base class for SQLAlchemy declarative base model.

    To define models, subclass :attr:`db.Model <SQLAlchemy.Model>`, not this
    class. To customize ``db.Model``, subclass this and pass it as
    ``model_class`` to :class:`SQLAlchemy`.
    """

    #: Query class used by :attr:`query`. Defaults to
    # :class:`SQLAlchemy.Query`, which defaults to :class:`BaseQuery`.
    query_class = None

    #: Convenience property to query the database for instances of this model
    # using the current session. Equivalent to ``self.fsa_session.query(Model)``
    # unless :attr:`query_class` has been changed.
    query = None
    
    _fsa = None


    @classmethod
    def columns(cls):
        tbl = getattr(cls, "__table__", None)
        if tbl is None:
            name = cls.__name__
            msg = f'Failed to Access "{name}.__table__", it should be registered as A DeclarativeModel.'
            logger.exception(msg)
            raise FsaAdaptError(msg, model_class=cls)
        else:
            return tbl.columns

    @classmethod
    def primary_keys(cls):
        tbl = cls.__table__
        pks = [m.name for m in tbl.primary_key.columns]
        return pks

    @classmethod
    def _immutable_keys(cls):
        # limit columns should not updated by cls.update(form)
        pks = cls.primary_keys()
        return pks

    @classmethod
    def strict_form(cls, data=None, **kwargs):
        col_ = getattr(cls, "data", None)
        if isinstance(col_, InstrumentedAttribute):
            kwargs.update(data=data)
        else:
            if data is None:
                pass
            elif isinstance(data, dict):
                kwargs.update(data)
            else:
                raise FsaAdaptError('data value must be dict or None')

        form = {}
        for k, v in kwargs.items():
            col = getattr(cls, k, None)
            if isinstance(col, InstrumentedAttribute):
                form[k] = v
        return form

    @classmethod
    def initial(cls, data=None, **kwargs):
        form = cls.strict_form(data, **kwargs)
        m = cls(**form)
        return m

    @classmethod
    def insert(cls, data=None, **kwargs):
        m = cls.initial(data, **kwargs)
        m.save()
        return m

    @classmethod
    def _make_query(cls, condition=None, limit=None, offset=None, order_by=None, **condition_kws):
        # NOTE: ERROR raise if call query.[update({})/delete()] after limit()/offset()/distinct()/group_by()/order_by()
        condition = cls.strict_form(condition, **condition_kws)
        qry = cls.query.filter_by(**condition)
        if isinstance(order_by, (list, tuple)):
            qry = qry.order_by(*order_by)
        elif order_by is not None:
            # NOTE: Raise Error if bool(order_by)
            qry = qry.order_by(order_by)
        if isinstance(limit, int) and limit >= 0:
            qry = qry.limit(limit)
            if isinstance(offset, int) and offset >= 0:
                qry = qry.offset(offset)
        return qry

    @classmethod
    def discard(cls, condition=None, limit=1, **condition_kws):
        # In Case of incorrect operation, default limit 1;
        condition = cls.strict_form(condition, **condition_kws)
        with cls.fsa_lock():
            db_sess = cls.fsa_session
            # n = cls.query.filter_by(**condition).delete()
            n = db_sess.query(cls).filter_by(**condition).delete()
            if limit > 0 and limit < n:
                db_sess.rollback()
                msg = "You're trying discard {} rows of {}, which is over limit={}".format(n, cls.__name__, limit)
                raise FsaAdaptError(msg)
            else:
                db_sess.commit()
            return n

    @classmethod
    def page_items(cls, condition=None, limit=10, offset=0, order_by=None, **condition_kws):
        qry = cls._make_query(condition, **condition_kws)
        pk = cls.primary_keys()[0]
        total = qry.value(func.count(getattr(cls, pk)))
        if isinstance(order_by, (list, tuple)):
            qry = qry.order_by(*order_by)
        elif order_by is not None:
            qry = qry.order_by(order_by)
        if limit > 0:
            items = qry.limit(limit).offset(offset).all()
        elif limit == 0:
            items = []
        else:
            items = qry.all()
        next_offset = offset + len(items)
        has_more = total > next_offset
        return dict(total=total, limit=limit, next_offset=next_offset, has_more=has_more, items=items)

    @classmethod
    def filter_by(cls, condition=None, **condition_kws):
        qry = cls._make_query(condition, **condition_kws)
        ms = qry.all()
        return ms

    @classmethod
    def count(cls, condition=None, **condition_kws):
        # https://docs.sqlalchemy.org/en/latest/orm/query.html#sqlalchemy.orm.query.Query.count
        qry = cls._make_query(condition, **condition_kws)
        pk = cls.primary_keys()[0]
        qry = qry.value(func.count(getattr(cls, pk)))
        return qry

    @classmethod
    def get_or_none(cls, condition=None, **condition_kws):
        cond = cls.strict_form(condition, **condition_kws)
        return cls.query.filter_by(**cond).one_or_none()

    @classmethod
    def upsert_one(cls, condition: dict, **updated_kws):
        m = cls.get_or_none(condition)
        if isinstance(m, cls):
            m.update(updated_kws)
        else:
            m = cls.insert(condition, **updated_kws)
        return m

    @classmethod
    def getOr404(cls, **condition_kws):
        m = cls.get_or_none(condition_kws)
        if isinstance(m, cls):
            return m
        else:
            name = cls.__name__
            msg = f"[{name}]Data Not Found: {condition_kws}"
            raise FsaAdaptError(msg, errno=40420, status_code=404)

    def to_dict(self, **kwargs):
        d = dict(_type=self.__class__.__name__)
        columns = self.columns()
        for col in columns:
            name = col.name
            value = getattr(self, name)
            d[name] = value
        d.update(kwargs)
        return d

    def update(self, form=None, __force=False, **kwargs):
        data = self.strict_form(form, **kwargs)
        keys = self._immutable_keys()
        is_modified = False
        for k, v in data.items():
            is_mutable = k not in keys
            if __force or is_mutable:
                is_modified = True
                setattr(self, k, v)
                if isinstance(v, (dict, list, tuple)):
                    flag_modified(self, k)
            else:
                v0 = getattr(self, k, None)
                tp = self.__class__.__name__
                msg = "Immutable Field {}.{}, ignore updating `{} => {}`".format(tp, k, v0, v)
                logger.warning(msg)
        if is_modified:
            self.fsa_session.commit()

    def save(self):
        self.fsa_session.add(self)
        self.fsa_session.commit()

    def remove(self):
        self.fsa_session.delete(self)
        self.fsa_session.commit()


class CoModel(ExtModel):

    @declared_attr
    def created_time(self):
        return CoField(DateTimeLZ, default=utils.now)

    @declared_attr
    def updated_time(self):
        return CoField(DateTimeLZ, default=utils.now, onupdate=utils.now)


    @classmethod
    def lastOrNone(cls, **kwargs):
        order_by = kwargs.pop("order_by", cls.created_time.desc())
        qry = cls._make_query(kwargs, limit=1, order_by=order_by)
        return qry.one_or_none()

    @classmethod
    def lastOr404(cls, **kwargs):
        m = cls.lastOrNone(**kwargs)
        if isinstance(m, cls):
            return m
        msg = "Data Not Found: {}: {}".format(cls.__name__, pformat(kwargs))
        raise FsaAdaptError(msg, errno=40400)
