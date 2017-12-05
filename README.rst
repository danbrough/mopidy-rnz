****************************
Mopidy-RNZ
****************************

.. image:: https://img.shields.io/pypi/v/Mopidy-RNZ.svg?style=flat
    :target: https://pypi.python.org/pypi/Mopidy-RNZ/
    :alt: Latest PyPI version

.. image:: https://img.shields.io/travis/danbrough/mopidy-rnz/master.svg?style=flat
    :target: https://travis-ci.org/danbrough/mopidy-rnz
    :alt: Travis CI build status

.. image:: https://img.shields.io/coveralls/danbrough/mopidy-rnz/master.svg?style=flat
   :target: https://coveralls.io/r/danbrough/mopidy-rnz
   :alt: Test coverage

Mopidy extension for RNZ content

This backend extension provides access to the podcasts, live-streams and the latest news bulletin


Installation
============

Install by running::

    pip install Mopidy-RNZ

Or, if available, install the Debian/Ubuntu package from `apt.mopidy.com
<http://apt.mopidy.com/>`_.


Configuration
=============

Before starting Mopidy, you must add configuration for
Mopidy-RNZ to your Mopidy configuration file::

    [rnz]
    enabled = true
    # default value for where http pages are cached
    #http_cache = ~/.rnz_cache



Project resources
=================

- `Source code <https://github.com/danbrough/mopidy-rnz>`_
- `Issue tracker <https://github.com/danbrough/mopidy-rnz/issues>`_


Credits
=======

- Original author: `Dan Brough <https://github.com/danbrough`__
- Current maintainer: `Dan Brough <https://github.com/danbrough`__
- `Contributors <https://github.com/danbrough/mopidy-rnz/graphs/contributors>`_


Changelog
=========

v0.1.0 (UNRELEASED)
----------------------------------------

- Initial release.
- Basic streams are available but haven't implemented podcasts yet.
