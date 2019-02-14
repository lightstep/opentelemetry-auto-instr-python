"""
"""

from ...utils.importlib import require_modules

required_modules = ['gunicorn']

with require_modules(required_modules) as missing_modules:
    if not missing_modules:
        # DEV: We do this so we can `@mock.patch('ddtrace.contrib.gunicorn._patch.<func>')` in tests
        from . import patch as _patch

        patch = _patch.patch
        unpatch = _patch.unpatch

        __all__ = ['patch', 'unpatch']
