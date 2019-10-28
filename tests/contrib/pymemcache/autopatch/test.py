import pymemcache
import unittest
from oteltrace.vendor import wrapt


class AutoPatchTestCase(unittest.TestCase):
    """Test ensuring that oteltrace-run patches pymemcache.

    This ensures that things like the patch functions are properly exported
    from the module and used to patch the library.

    Note: you may get cryptic errors due to oteltrace-run failing, such as

        Traceback (most recent call last):
        File ".../dev/otel-trace-py/tests/contrib/pymemcache/test_autopatch.py", line 8, in test_patch
        assert issubclass(pymemcache.client.base.Client, wrapt.ObjectProxy)
        AttributeError: 'module' object has no attribute 'client'

    this is indicitive of the patch function not being exported by the module.
    """

    def test_patch(self):
        assert issubclass(pymemcache.client.base.Client, wrapt.ObjectProxy)
