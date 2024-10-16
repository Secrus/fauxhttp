# #!/usr/bin/env python
# -*- coding: utf-8 -*-

# <HTTPretty - HTTP client mock for Python>
# Copyright (C) <2011-2021> Gabriel Falcão <gabriel@nacaolivre.org>
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation
# files (the "Software"), to deal in the Software without
# restriction, including without limitation the rights to use,
# copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following
# conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
import io
import os
from setuptools import setup, find_packages


local_file = lambda *f: \
    io.open(
        os.path.join(os.path.dirname(__file__), *f), encoding='utf-8').read()


setup(
    name='fauxhttp',
    version="0.1.0",
    description='HTTP client mock for Python',
    long_description=local_file('README.rst'),
    author='Gabriel Falcao',
    author_email='gabriel@nacaolivre.org',
    url='https://httpretty.readthedocs.io/en/latest/',
    zip_safe=False,
    packages=find_packages(exclude=['*tests*']),
    tests_require=local_file('development.txt').splitlines(),
    install_requires=[],
    license='MIT',
    test_suite='nose.collector',
    project_urls={
        "Documentation": "https://httpretty.readthedocs.io/en/latest/",
        "Source Code": "https://github.com/Secrus/fauxhttp",
        "Issue Tracker": "https://github.com/Secrus/fauxhttp/issues",
    },
    python_requires='>=3.9',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Testing'
    ],
)
