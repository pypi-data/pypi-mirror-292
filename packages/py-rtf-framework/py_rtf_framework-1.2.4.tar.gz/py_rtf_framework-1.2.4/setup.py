#!/usr/bin/env python
# -*- coding:utf-8 -*-
import os
from setuptools import setup, find_packages

MAJOR = 1
MINOR = 2
PATCH = 4
VERSION = f"{MAJOR}.{MINOR}.{PATCH}"


def get_install_requires():
    reqs = [
        'pyyaml==6.0.1',
        "pydantic==2.8.2",
        "aiofiles==24.1.0",
        "pandas==2.2.2",
        "numba==0.60.0",
        "swifter==1.4.0",
        "aiolimiter==1.1.0",
        "flask==3.0.3",
        "langchain-community==0.2.10",
        "clickhouse-driver==0.2.8",
        "clickhouse-sqlalchemy==0.3.2",
        "elastic-transport==8.13.1",
        "elasticsearch==8.14.0",
        "langchain-core==0.2.33",
        "langchain-elasticsearch==0.2.2",
        "networkx==3.3",
        "sqlalchemy==2.0.31",
        "pymysql==1.1.1",
        "asyncio==3.4.3",
        "tqdm==4.66.4",
        "pyotp==2.9.0",
        "matplotlib==3.9.1",
        "cachetools==5.4.0",
        "diskcache==5.6.3",
        "jsonschema==4.23.0",
        "tenacity==8.5.0",
        "dashscope==1.20.4",
        "apscheduler==3.10.4"
    ]
    return reqs


setup(
    name="py_rtf_framework",
    version=VERSION,
    author="liupeng",
    author_email="895876294@qq.com",
    long_description_content_type="text/markdown",
    url='',
    long_description=open('README.md', encoding="utf-8").read(),
    python_requires=">=3.11",
    install_requires=get_install_requires(),
    packages=find_packages(),
    license='Apache',
    classifiers=[
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.11',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    package_data={'': ['*.csv', '*.txt', '.toml']},  # 这个很重要
    include_package_data=True
)
