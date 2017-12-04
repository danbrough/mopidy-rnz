from __future__ import unicode_literals

import re

from setuptools import find_packages, setup


def get_version(filename):
    with open(filename) as fh:
        metadata = dict(re.findall("__([a-z]+)__ = '([^']+)'", fh.read()))
        return metadata['version']


setup(
    name='Mopidy-RNZ',
    version=get_version('mopidy_rnz/__init__.py'),
    url='https://github.com/danbrough/mopidy-rnz',
    license='Apache License, Version 2.0',
    author='Dan Brough',
    author_email='dan@danbrough.org',
    description='Mopidy extension for RNZ content',
    long_description=open('README.rst').read(),
    packages=find_packages(exclude=['tests', 'tests.*']),
    zip_safe=False,
    include_package_data=True,
    install_requires=[
        'setuptools',
        'Mopidy >= 1.0',
        'Pykka >= 1.1',
        'requests-cache >= 0.4.13',
    ],
    entry_points={
        'mopidy.ext': [
            'rnz = mopidy_rnz:Extension',
        ],
    },
    classifiers=[
        'Environment :: No Input/Output (Daemon)',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Topic :: Multimedia :: Sound/Audio :: Players',
    ],
)
