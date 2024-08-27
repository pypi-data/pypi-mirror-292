# -*- coding: utf-8 -*-
from __future__ import absolute_import
import sqlalchemy  # noqa

## @formatter:off
from . import utils, _adapt, _compat
from ._compat import itervalues, string_types, xrange
from ._signals import before_models_committed, signals_available, models_committed
from ._langhelp import get_attr_of_package
from ._adapt import FsaAdaptError, FSADeprecationWarning, FsaAppAdaptor

from .model import DefaultMeta
from .model import Model
from .exports import SQLAlchemy

from .plugins._flask import FlaskSqlalchemy


__Copyrights_Of_Forked_Repos = {
    ##; Copyright (c) 2010-2021, Armin Ronacher(BSD-3-Clause)
    "flask-sqlalchemy": dict(
        version="2.5.1",
        RepoUrl="https://github.com/pallets-eco/flask-sqlalchemy/tree/2.5.1",
        License="BSD-3-Clause"
    )
}
## @formatter:on

version_info = (2, 5, 8)
__version__ = "2.5.8"

__all__ = [
    sqlalchemy,
    SQLAlchemy,
    Model,
    DefaultMeta,
    FsaAdaptError,
    FSADeprecationWarning,
]
