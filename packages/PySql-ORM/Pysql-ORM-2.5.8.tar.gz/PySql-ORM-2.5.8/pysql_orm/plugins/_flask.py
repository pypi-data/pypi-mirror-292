# -*- coding: utf-8 -*-
"""
#/*
##; Copyright (c) 2010-2021, Armin Ronacher(BSD-3-Clause)
##; All rights reserved.
##; 
##; @@@Origin: https://github.com/pallets-eco/flask-sqlalchemy/blob/2.5.1/flask_sqlalchemy/__init__.py
##; 
##; This module is part of SQLAlchemy and is released under
##; the BSD-3-Clause License: https://opensource.org/license/bsd-3-clause
##; details as below:
#*
#* Redistribution and use in source and binary forms, with or without
#* modification, are permitted provided that the following conditions are met:
#*
#* 1. Redistributions of source code must retain the above copyright notice, this
#*    list of conditions and the following disclaimer.
#*
#* 2. Redistributions in binary form must reproduce the above copyright notice,
#*    this list of conditions and the following disclaimer in the documentation
#*    and/or other materials provided with the distribution.
#*
#* 3. Neither the name of the copyright holder nor the names of its
#*    contributors may be used to endorse or promote products derived from
#*    this software without specific prior written permission.
#*
#* THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
#* AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
#* IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
#* DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
#* FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
#* DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
#* SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
#* CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
#* OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
#* OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#*/
"""

from __future__ import absolute_import
import warnings
from sqlalchemy import orm
from math import ceil
import flask

from .._compat import xrange
from ..exports import SQLAlchemy


def get_debug_queries():
    """In debug mode Flask-SQLAlchemy will log all the SQL queries sent
    to the database.  This information is available until the end of request
    which makes it possible to easily ensure that the SQL generated is the
    one expected on errors or in unittesting.  If you don't want to enable
    the DEBUG mode for your unittests you can also enable the query
    recording by setting the ``'SQLALCHEMY_RECORD_QUERIES'`` config variable
    to `True`.  This is automatically enabled if Flask is in testing mode.

    The value returned will be a list of named tuples with the following
    attributes:

    `statement`
        The SQL statement issued

    `parameters`
        The parameters for the SQL statement

    `start_time` / `end_time`
        Time the query started / the results arrived.  Please keep in mind
        that the timer function used depends on your platform. These
        values are only useful for sorting or comparing.  They do not
        necessarily represent an absolute timestamp.

    `duration`
        Time the query took in seconds

    `context`
        A string giving a rough estimation of where in your application
        query was issued.  The exact format is undefined so don't try
        to reconstruct filename or function name.

    ===============================        
    .. versionchanged:: 2.5.3 (pysql-orm)    
        refactor from <flask_sqlalchemy.get_debug_queries> to <pysql_orm.exts._flask.get_debug_queries>
        
    """
    if flask.has_app_context():
        return getattr(flask._app_ctx_stack.top, 'sqlalchemy_queries', [])
    return []


class Pagination(object):
    """Internal helper class returned by :meth:`BaseQuery.paginate`.  You
    can also construct it from any other SQLAlchemy query object if you are
    working with other libraries.  Additionally it is possible to pass `None`
    as query object in which case the :meth:`prev` and :meth:`next` will
    no longer work.
    """

    def __init__(self, query, page, per_page, total, items):
        #: the unlimited query object that was used to create this
        #: pagination object.
        self.query = query
        #: the current page number (1 indexed)
        self.page = page
        #: the number of items to be displayed on a page.
        self.per_page = per_page
        #: the total number of items matching the query
        self.total = total
        #: the items for the current page
        self.items = items

    @property
    def pages(self):
        """The total number of pages"""
        if self.per_page == 0:
            pages = 0
        else:
            pages = int(ceil(self.total / float(self.per_page)))
        return pages

    def prev(self, error_out=False):
        """Returns a :class:`Pagination` object for the previous page."""
        assert self.query is not None, 'a query object is required ' \
                                       'for this method to work'
        return self.query.paginate(self.page - 1, self.per_page, error_out)

    @property
    def prev_num(self):
        """Number of the previous page."""
        if not self.has_prev:
            return None
        return self.page - 1

    @property
    def has_prev(self):
        """True if a previous page exists"""
        return self.page > 1

    def next(self, error_out=False):
        """Returns a :class:`Pagination` object for the next page."""
        assert self.query is not None, 'a query object is required ' \
                                       'for this method to work'
        return self.query.paginate(self.page + 1, self.per_page, error_out)

    @property
    def has_next(self):
        """True if a next page exists."""
        return self.page < self.pages

    @property
    def next_num(self):
        """Number of the next page"""
        if not self.has_next:
            return None
        return self.page + 1

    def iter_pages(self, left_edge=2, left_current=2,
                   right_current=5, right_edge=2
                   ):
        """Iterates over the page numbers in the pagination.  The four
        parameters control the thresholds how many numbers should be produced
        from the sides.  Skipped page numbers are represented as `None`.
        This is how you could render such a pagination in the templates:

        .. sourcecode:: html+jinja

            {% macro render_pagination(pagination, endpoint) %}
              <div class=pagination>
              {%- for page in pagination.iter_pages() %}
                {% if page %}
                  {% if page != pagination.page %}
                    <a href="{{ url_for(endpoint, page=page) }}">{{ page }}</a>
                  {% else %}
                    <strong>{{ page }}</strong>
                  {% endif %}
                {% else %}
                  <span class=ellipsis>…</span>
                {% endif %}
              {%- endfor %}
              </div>
            {% endmacro %}
        """
        last = 0
        for num in xrange(1, self.pages + 1):
            if num <= left_edge or \
                (num > self.page - left_current - 1 and
                 num < self.page + right_current) or \
                num > self.pages - right_edge:
                if last + 1 != num:
                    yield None
                yield num
                last = num


class FsaQuery(orm.Query):
    """SQLAlchemy :class:`~sqlalchemy.orm.query.Query` subclass with convenience methods for querying in a web application.

    This is the default :attr:`~Model.query` object used for models, and exposed as :attr:`~SQLAlchemy.Query`.
    Override the query class for an individual model by subclassing this and setting :attr:`~Model.query_class`.
    -----
    .. versionadded:: 0.5  
        <BaseModel>: Added before flask-sqlaclhemy==0.5 
        @commit_id: 15dfb4854ed3f11056da75aa7a8816943e42780b
    
    .. versionchanged:: 2.5.3 (pysql-orm)    
        refactor from <flask_sqlalchemy.BaseModel> to <pysql_orm.exts._flask.FsaQuery>
        
        
    """

    def get_or_404(self, ident, description=None):
        """Like :meth:`get` but aborts with 404 if not found instead of returning ``None``."""

        rv = self.get(ident)
        if rv is None:
            flask.abort(404, description=description)
        return rv

    def first_or_404(self, description=None):
        """Like :meth:`first` but aborts with 404 if not found instead of returning ``None``."""

        rv = self.first()
        if rv is None:
            flask.abort(404, description=description)
        return rv

    def paginate(self, page=None, per_page=None, error_out=True, max_per_page=None):
        """Returns ``per_page`` items from page ``page``.

        If ``page`` or ``per_page`` are ``None``, they will be retrieved from
        the request query. If ``max_per_page`` is specified, ``per_page`` will
        be limited to that value. If there is no request or they aren't in the
        query, they default to 1 and 20 respectively.

        When ``error_out`` is ``True`` (default), the following rules will
        cause a 404 response:

        * No items are found and ``page`` is not 1.
        * ``page`` is less than 1, or ``per_page`` is negative.
        * ``page`` or ``per_page`` are not ints.

        When ``error_out`` is ``False``, ``page`` and ``per_page`` default to
        1 and 20 respectively.

        Returns a :class:`Pagination` object.
        """

        if flask.has_request_context():
            request = flask.request
            if page is None:
                try:
                    page = int(request.args.get('page', 1))
                except (TypeError, ValueError):
                    if error_out:
                        flask.abort(404)

                    page = 1

            if per_page is None:
                try:
                    per_page = int(request.args.get('per_page', 20))
                except (TypeError, ValueError):
                    if error_out:
                        flask.abort(404)

                    per_page = 20
        else:
            if page is None:
                page = 1

            if per_page is None:
                per_page = 20

        if max_per_page is not None:
            per_page = min(per_page, max_per_page)

        if page < 1:
            if error_out:
                flask.abort(404)
            else:
                page = 1

        if per_page < 0:
            if error_out:
                flask.abort(404)
            else:
                per_page = 20

        items = self.limit(per_page).offset((page - 1) * per_page).all()

        if not items and page != 1 and error_out:
            flask.abort(404)

        total = self.order_by(None).count()

        return Pagination(self, page, per_page, total, items)


class FlaskSqlalchemy(SQLAlchemy):
    """This class is used to control the SQLAlchemy integration to one
        or more Flask applications.  Depending on how you initialize the
        object it is usable right away or will attach as needed to a
        Flask application.

        There are two usage modes which work very similarly.  One is binding
        the instance to a very specific Flask application::

            app = Flask(__name__)
            db = SQLAlchemy(app)

        The second possibility is to create the object once and configure the
        application later to support it::

            db = SQLAlchemy()

            def create_app():
                app = Flask(__name__)
                db.init_app(app)
                return app

        The difference between the two is that in the first case methods like
        :meth:`create_all` and :meth:`drop_all` will work all the time but in
        the second case a :meth:`flask.Flask.app_context` has to exist.

        By default Flask-SQLAlchemy will apply some backend-specific settings
        to improve your experience with them.

        As of SQLAlchemy 0.6 SQLAlchemy
        will probe the library for native unicode support.  If it detects
        unicode it will let the library handle that, otherwise do that itself.
        Sometimes this detection can fail in which case you might want to set
        ``use_native_unicode`` (or the ``SQLALCHEMY_NATIVE_UNICODE`` configuration
        key) to ``False``.  Note that the configuration key overrides the
        value you pass to the constructor.  Direct support for ``use_native_unicode``
        and SQLALCHEMY_NATIVE_UNICODE are deprecated as of v2.4 and will be removed
        in v3.0.  ``engine_options`` and ``SQLALCHEMY_ENGINE_OPTIONS`` may be used
        instead.

        This class also provides access to all the SQLAlchemy functions and classes
        from the :mod:`sqlalchemy` and :mod:`sqlalchemy.orm` modules.  So you can
        declare models like this::

            class User(db.Model):
                username = db.Column(db.String(80), unique=True)
                pw_hash = db.Column(db.String(80))

        You can still use :mod:`sqlalchemy` and :mod:`sqlalchemy.orm` directly, but
        note that Flask-SQLAlchemy customizations are available only through an
        instance of this :class:`SQLAlchemy` class.  Query classes default to
        :class:`BaseQuery` for `db.Query`, `db.Model.query_class`, and the default
        query_class for `db.relationship` and `db.backref`.  If you use these
        interfaces through :mod:`sqlalchemy` and :mod:`sqlalchemy.orm` directly,
        the default query class will be that of :mod:`sqlalchemy`.

        .. admonition:: Check types carefully

           Don't perform type or `isinstance` checks against `db.Table`, which
           emulates `Table` behavior but is not a class. `db.Table` exposes the
           `Table` interface, but is a function which allows omission of metadata.

        The ``session_options`` parameter, if provided, is a dict of parameters
        to be passed to the session constructor.  See :class:`~sqlalchemy.orm.session.Session`
        for the standard options.

        The ``engine_options`` parameter, if provided, is a dict of parameters
        to be passed to create engine.  See :func:`~sqlalchemy.create_engine`
        for the standard options.  The values given here will be merged with and
        override anything set in the ``'SQLALCHEMY_ENGINE_OPTIONS'`` config
        variable or othewise set by this library.

        .. versionadded:: 0.10
           The `session_options` parameter was added.

        .. versionadded:: 0.16
           `scopefunc` is now accepted on `session_options`. It allows specifying
            a custom function which will define the SQLAlchemy session's scoping.

        .. versionadded:: 2.1
           The `metadata` parameter was added. This allows for setting custom
           naming conventions among other, non-trivial things.

           The `query_class` parameter was added, to allow customisation
           of the query class, in place of the default of :class:`BaseQuery`.

           The `model_class` parameter was added, which allows a custom model
           class to be used in place of :class:`Model`.

        .. versionchanged:: 2.1
           Utilise the same query class across `session`, `Model.query` and `Query`.

        .. versionadded:: 2.4
           The `engine_options` parameter was added.

        .. versionchanged:: 2.4
           The `use_native_unicode` parameter was deprecated.

        .. versionchanged:: 2.4.3
            ``COMMIT_ON_TEARDOWN`` is deprecated and will be removed in
            version 3.1. Call ``db.session.commit()`` directly instead.

        ========================================================
        ##; flask-sqlalchemy==2.5.1 >>> PysqlOrm==2.5.3 
        ========================================================    
        .. versionchanged:: 2.5.3
            query_class change defaults from class:`BaseQuery(FsaQuery)` to `orm.Query`
            lazyload with default as None 

        """

    #: Default query class used by :attr:`Model.query` and other queries.
    #: Customize this by passing ``query_class`` to :func:`SQLAlchemy`.
    _QueryClass = FsaQuery
    _app_framework = "flask"

    def init_app(self, app, cfg=None, app_framework="flask"):
        self._init_app(app, cfg=cfg)
        self._app_framework = app_framework

        @app.teardown_appcontext
        def shutdown_session(response_or_exc):
            if self.cfg_option('SQLALCHEMY_COMMIT_ON_TEARDOWN'):
                warnings.warn(
                    "'COMMIT_ON_TEARDOWN' is deprecated and will be"
                    " removed in version 3.1. Call"
                    " 'db.session.commit()'` directly instead.",
                    DeprecationWarning,
                )

                if response_or_exc is None:
                    self.session.commit()

            self.session.remove()
            return response_or_exc


    def get_app(self, reference_app=None, nullable=False):
        if reference_app is not None:
            return reference_app
        if flask.has_app_context():
            return flask.current_app  # type: flask.Flask

        if self._app is not None:
            return self._app
        if nullable:
            return None

        raise RuntimeError(
            'No application found. '
            'Either work inside a view function or push an application context. '
            'See  http://flask-sqlalchemy.pocoo.org/contexts/.'
        )
