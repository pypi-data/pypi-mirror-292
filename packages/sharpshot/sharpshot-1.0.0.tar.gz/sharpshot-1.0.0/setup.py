#!/usr/bin/env python
from setuptools import find_packages
from setuptools import setup

from sharpshot import __version__, __description__

with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="sharpshot",
    version=__version__,
    keywords=["sharpshot", "test", "static-code-analysis", "tools"],
    description=__description__,
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="Apache License 2.0",
    url="https://github.com/openutx",
    author="lijiawei",
    author_email="jiawei.li2@qq.com",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console :: Curses",
        "Operating System :: MacOS",
        "Operating System :: POSIX",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: Implementation :: CPython",
    ],
    entry_points="""
    [console_scripts]
    sharpshot = sharpshot.run:sharp_shot
    """,
    packages=find_packages(),
    include_package_data=True,
    platforms="any",
    install_requires=[
        "javalang==0.13.0",
        "unidiff~=0.7.4",
        "jinja2",
        "requests",
    ],
)
