#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

from __meta__ import __version__, __author__, __email__

with open('README.rst') as readme_file:
    README = readme_file.read()

if os.path.exists("HISTORY.rst"):
    with open('HISTORY.rst') as history_file:
        HISTORY = history_file.read().replace('.. :changelog:', '')
else:
    HISTORY = ""

REQUIREMENTS = [
    "celery==3.1.19",
    "requests==2.8.1",
]

TEST_REQUIREMENTS = [
    'nose',
]

setup(
    # -- meta information --------------------------------------------------
    name='Service',
    version=__version__,
    description="Code to facilitate creation of services and their "
                "integration to Vesta Service Gateway.",
    long_description=README + '\n\n' + HISTORY,
    author=__author__,
    author_email=__email__,
    url='https://github.com/crim-ca/Service',
    platforms=['linux_x86_64'],
    license="Apache 2.0",
    keywords='Vesta,Service',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Version 2.0',
        'Natural Language :: English',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],

    # -- Package structure -------------------------------------------------
    packages=[
        'Service'
    ],
    package_dir={'Service': '.'},
    include_package_data=True,
    install_requires=REQUIREMENTS,
    zip_safe=False,

    # -- self - tests --------------------------------------------------------
    test_suite='tests',
    tests_require=TEST_REQUIREMENTS,

    # -- script entry points -----------------------------------------------
    entry_points={'console_scripts':
                  ["send_annotation=Service.annotations_dispatcher:main",
                   "send_request=Service.request_process_mesg:main"]}
)
