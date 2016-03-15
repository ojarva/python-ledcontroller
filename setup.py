"""
Packaging setup for ledcontroller
"""

# pylint: disable=line-too-long

import os.path
from codecs import open as codecs_open
from setuptools import setup

with codecs_open(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'README.rst'), encoding='utf-8') as f:
    LONG_DESCRIPTION = f.read()

setup(
    name='ledcontroller',
    version='1.3.0',
    description='Controller library for limitlessled/easybulb/milight Wi-Fi LEDs',
    long_description=LONG_DESCRIPTION,
    url='https://github.com/ojarva/python-ledcontroller',
    author='Olli Jarva',
    author_email='olli@jarva.fi',
    license='BSD',

    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Topic :: Home Automation',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',

        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: Implementation :: PyPy',
    ],
    keywords='applight applamp dekolight easybulb ilight limitlessled led ledme milight wifi',
    packages=["ledcontroller"],
    install_requires=[],
    test_suite="tests",

    extras_require={
        'dev': ['twine', 'wheel'],
    },
)
