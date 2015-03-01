from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='ledcontroller',
    version='1.1.0',
    description='Controller library for limitlessled/easybulb/milight Wi-Fi LEDs',
    long_description=long_description,
    url='https://github.com/ojarva/python-ledcontroller',
    author='Olli Jarva',
    author_email='olli@jarva.fi',
    license='BSD',

    classifiers=[
        'Development Status :: 4 - Beta',
        'Topic :: Home Automation',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',

        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
    keywords='limitlessled easybulb milight led wifi',
    packages=["ledcontroller"],
    install_requires=[],
    test_suite="tests",

    extras_require = {
        'dev': ['twine', 'wheel'],
    },
)
