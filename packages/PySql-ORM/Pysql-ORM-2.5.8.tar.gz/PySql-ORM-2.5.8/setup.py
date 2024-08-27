import io

from setuptools import setup
import re

with io.open("README.rst", "rt", encoding="utf8") as f:
    readme = f.read()

with io.open("pysql_orm/__init__.py", "rt", encoding="utf8") as f:
    version_str = re.search(r'__version__ = "(.*?)"', f.read(), re.M).group(1)

setup(
    # name="Flask-SQLAlchemy",
    name="PySql-ORM",
    version=version_str,
    url="https://github.com/dodoru/pysql-orm",
    # project_urls={
    #     "Documentation": "https://flask-sqlalchemy.palletsprojects.com/",
    #     "Code": "https://github.com/pallets/flask-sqlalchemy",
    #     "Issue tracker": "https://github.com/pallets/flask-sqlalchemy/issues",
    # },
    license="BSD-3-Clause",
    author="Armin Ronacher",
    author_email="armin.ronacher@active-4.com",
    maintainer="dodoru",
    maintainer_email="dodoru@foxmail.com",
    description="Adapt SQLAlchemy ORM Support to web application, include Flask, Django, or any other web frameworks. A Fork GitRepo from: https://github.com/pallets/flask-sqlalchemy",
    long_description=readme,
    packages=["pysql_orm"],
    include_package_data=True,
    python_requires=">= 2.7, != 3.0.*, != 3.1.*, != 3.2.*, != 3.3.*",
    # install_requires=["Flask>=0.10", "SQLAlchemy>=0.8.0"],
    install_requires=[
            "Flask", 
            "SQLAlchemy<2.0",
            "pyco-types",
    ],
    classifiers=[
        ##; https://pypi.org/classifiers/
        ##; "Development Status :: 4 - Beta",
        ##;(1, ".dev" ,"Development Status :: 1 - Planning",), 
        ##;(1, ".post" ,"Development Status :: 1 - Planning",),
        ##;(2, "a" ,"Development Status :: 2 - Pre-Alpha",),
        ##;(3, "a" ,"Development Status :: 3 - Alpha",),
        ##;(4, "b" ,"Development Status :: 4 - Beta",),
        ##;(5, "rc" ,"Development Status :: 5 - Production/Stable",),
        ##;(6, "" ,"Development Status :: 6 - Mature",),
        ##;(7, "" ,"Development Status :: 7 - Inactive",),
        "Development Status :: 1 - Planning",
        # "ENVIRONMENT :: PLUGINS",
        "Environment :: Web Environment",
        # "NATURAL LANGUAGE :: ENGLISH",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        # "PROGRAMMING LANGUAGE :: SQL",
        "Topic :: Utilities",
        # "TOPIC :: DATABASE :: FRONT-ENDS",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
