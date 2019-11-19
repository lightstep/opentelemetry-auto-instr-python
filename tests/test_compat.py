# -*- coding: utf-8 -*-
# Copyright 2019, OpenTelemetry Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Define source file encoding to support raw unicode characters in Python 2
import sys

# Third party
import pytest

# Project
from oteltrace.compat import to_unicode, PY3, reraise, get_connection_response


if PY3:
    unicode = str


class TestCompat(object):

    def test_to_unicode_string(self):
        # Calling `compat.to_unicode` on a non-unicode string
        res = to_unicode(b'test')
        assert type(res) == unicode
        assert res == 'test'

    def test_to_unicode_unicode_encoded(self):
        # Calling `compat.to_unicode` on a unicode encoded string
        res = to_unicode(b'\xc3\xbf')
        assert type(res) == unicode
        assert res == u'ÿ'

    def test_to_unicode_unicode_double_decode(self):
        # Calling `compat.to_unicode` on a unicode decoded string
        # This represents the double-decode issue, which can cause a `UnicodeEncodeError`
        #   `'\xc3\xbf'.decode('utf-8').decode('utf-8')`
        res = to_unicode(b'\xc3\xbf'.decode('utf-8'))
        assert type(res) == unicode
        assert res == u'ÿ'

    def test_to_unicode_unicode_string(self):
        # Calling `compat.to_unicode` on a unicode string
        res = to_unicode(u'ÿ')
        assert type(res) == unicode
        assert res == u'ÿ'

    def test_to_unicode_bytearray(self):
        # Calling `compat.to_unicode` with a `bytearray` containing unicode
        res = to_unicode(bytearray(b'\xc3\xbf'))
        assert type(res) == unicode
        assert res == u'ÿ'

    def test_to_unicode_bytearray_double_decode(self):
        #  Calling `compat.to_unicode` with an already decoded `bytearray`
        # This represents the double-decode issue, which can cause a `UnicodeEncodeError`
        #   `bytearray('\xc3\xbf').decode('utf-8').decode('utf-8')`
        res = to_unicode(bytearray(b'\xc3\xbf').decode('utf-8'))
        assert type(res) == unicode
        assert res == u'ÿ'

    def test_to_unicode_non_string(self):
        #  Calling `compat.to_unicode` on non-string types
        assert to_unicode(1) == u'1'
        assert to_unicode(True) == u'True'
        assert to_unicode(None) == u'None'
        assert to_unicode(dict(key='value')) == u'{\'key\': \'value\'}'

    def test_get_connection_response(self):
        """Ensure that buffering is in kwargs."""

        class MockConn(object):
            def getresponse(self, *args, **kwargs):
                if PY3:
                    assert 'buffering' not in kwargs
                else:
                    assert 'buffering' in kwargs

        mock = MockConn()
        get_connection_response(mock)


class TestPy2Py3Compat(object):
    """Common tests to ensure functions are both Python 2 and
    Python 3 compatible.
    """
    def test_reraise(self):
        # ensure the `raise` function is Python 2/3 compatible
        with pytest.raises(Exception) as ex:
            try:
                raise Exception('Ouch!')
            except Exception:
                # original exception we want to re-raise
                (typ, val, tb) = sys.exc_info()
                try:
                    # this exception doesn't allow a re-raise, and we need
                    # to use the previous one collected via `exc_info()`
                    raise Exception('Obfuscate!')
                except Exception:
                    pass
                # this call must be Python 2 and 3 compatible
                raise reraise(typ, val, tb)
        assert ex.value.args[0] == 'Ouch!'
