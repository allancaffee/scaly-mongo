#!/usr/bin/env python

import os
from setuptools import setup, find_packages


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name='scalymongo',
    version='0.1.2',
    description='A scaling-centric MongoDB object document mapper',
    keywords = 'mongo sharding db',
    url='https://github.com/allancaffee/scaly-mongo',
    author='Allan Caffee',
    author_email='allan.caffee@gmail.com',
    license='BSD',
    packages=['scalymongo'],
    install_requires=['pymongo>=1.9'],
    test_suite='tests',
    long_description=read('README.rst'),
    zip_safe=True,
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Topic :: Database',
    ],
)
