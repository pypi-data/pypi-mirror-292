PySql-ORM
================

Adapt to Support SQLAlchemy-ROM forweb application, 
include flask, django, or any other web frameworks.

--------

It is based on Flask-SQLAlchemy==2.5.1. which is extension for `Flask`_ 
that adds support for `SQLAlchemy`_ to your application. 
It aims to simplify using SQLAlchemy
with Flask by providing useful defaults and extra helpers that make it
easier to accomplish common tasks.


Installing
----------

Install and update using `pip`_:

.. code-block:: text

  $ pip install -U pysql-orm


A Simple Example
----------------

.. code-block:: python

    from flask import Flask
    from pysql_orm import SQLAlchemy

    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///example.sqlite"
    db = SQLAlchemy(app)


    class User(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        username = db.Column(db.String, unique=True, nullable=False)
        email = db.Column(db.String, unique=True, nullable=False)


    db.session.add(User(name="Flask", email="example@example.com"))
    db.session.commit()

    users = User.query.all()


Links
-----

-   Documentation: https://flask-sqlalchemy.palletsprojects.com/
-   Releases: https://pypi.org/project/Pysql-ORM/
-   Code: https://github.com/pallets/flask-sqlalchemy
-   Issue tracker: https://github.com/pallets/flask-sqlalchemy/issues
-   Test status: https://travis-ci.org/pallets/flask-sqlalchemy
-   Test coverage: https://codecov.io/gh/pallets/flask-sqlalchemy

.. _Flask: https://palletsprojects.com/p/flask/
.. _SQLAlchemy: https://www.sqlalchemy.org
.. _pip: https://pip.pypa.io/en/stable/quickstart/
