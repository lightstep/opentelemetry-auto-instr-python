"""
oteltrace.vendor
==============
Install vendored dependencies under a different top level package to avoid importing `oteltrace/__init__.py`
whenever a dependency is imported. Doing this allows us to have a little more control over import order.


Dependencies
============

six
---

Website: https://six.readthedocs.io/
Source: https://github.com/benjaminp/six
Version: 1.11.0
License: MIT

Notes:
  `six/__init__.py` is just the source code's `six.py`
  `curl https://raw.githubusercontent.com/benjaminp/six/1.11.0/six.py > oteltrace/vendor/six/__init__.py`


wrapt
-----

Website: https://wrapt.readthedocs.io/en/latest/
Source: https://github.com/GrahamDumpleton/wrapt/
Version: 1.11.1
License: BSD 2-Clause "Simplified" License

Notes:
  `wrapt/__init__.py` was updated to include a copy of `wrapt`'s license: https://github.com/GrahamDumpleton/wrapt/blob/1.11.1/LICENSE

  `setup.py` will attempt to build the `wrapt/_wrappers.c` C module


monotonic
---------

Website: https://pypi.org/project/monotonic/
Source: https://github.com/atdt/monotonic
Version: 1.5
License: Apache License 2.0

Notes:
  The source `monotonic.py` was added as `monotonic/__init__.py`

  No other changes were made
"""
