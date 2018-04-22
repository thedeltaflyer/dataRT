#!/usr/bin/env python
# -*- coding: utf-8 -*-
from codecs import open
from os.path import (abspath, dirname, join)
from subprocess import call

from setuptools import (Command, find_packages, setup)

from dataRT.version import __version__


this_dir = abspath(dirname(__file__))
with open(join(this_dir, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()


class RunTests(Command):
    """Run all tests."""

    description = 'run tests'
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        """Run all tests!"""
        err_no = call(['py.test', '--cov=kafka_tail_api', '--cov-report=term-missing'])
        raise SystemExit(err_no)


setup(
    name='dataRT',
    version=__version__,
    description='A Library for monitoring a datastream in real-time while writing data to WebSocket and InfluxDB',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/thedeltaflyer/dataRT',
    author='David Khudaverdyan',
    author_email='khudaverdyan.david@gmail.com',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
    ],
    keywords='websocket influxdb realtime',
    project_urls={
        'Source': 'https://github.com/thedeltaflyer/dataRT/',
        'Tracker': 'https://github.com/thedeltaflyer/dataRT/issues',
    },
    packages=find_packages(exclude=['docs', 'tests*']),
    install_requires=[
        'Flask>=0.12.2',
        'Flask-Sockets>=0.2.1',
        'gevent>=1.2.2',
        'influxdb>=5.0.0',
        'requests>=2.18.4'
    ],
    python_requires='~=3.6',
    extras_require={
        'test': ['coverage', 'pytest', 'pytest-cov'],
    },
    cmdclass={'test': RunTests},
)
