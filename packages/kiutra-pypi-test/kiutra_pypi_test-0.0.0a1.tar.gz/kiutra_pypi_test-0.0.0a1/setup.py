#!/usr/bin/env python
#  -*- coding: utf-8 -*-
#
# Copyright 2020 by kiutra GmbH
# All rights reserved.
# This file is part of Kiutra-Core

import sys
from setuptools import setup, find_packages

DISTNAME = "kiutra_pypi_test"
DESCRIPTION = "A python package to check how pypi packages work."
MAINTAINER = ""
MAINTAINER_EMAIL = ""
AUTHOR = 'kiutra GmbH'
AUTHOR_EMAIL = 'info@kiutra.com'
URL = ""
LICENSE = ""
DOWNLOAD_URL = ""
VERSION = '0.0.0'

requires = [
]


setup(
    name=DISTNAME,
    description=DESCRIPTION,
    maintainer=MAINTAINER,
    maintainer_email=MAINTAINER_EMAIL,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    url=URL,
    license=LICENSE,
    download_url=DOWNLOAD_URL,
    version=VERSION,
    packages=find_packages(),
    package_data={
        DISTNAME: ["*"],
    },
    include_package_data=True,
    install_requires=requires,
    classifiers=[
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
