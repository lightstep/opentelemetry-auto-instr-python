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

from webhelpers import *  # noqa


class ExceptionWithCodeMethod(Exception):
    """Use case where the status code is defined by
    the `code()` method.
    """
    def __init__(self, message):
        super(ExceptionWithCodeMethod, self).__init__(message)

    def code():
        pass


class AppGlobals(object):
    """Object used to store application globals."""
    pass


def get_render_fn():
    """Re-import the function everytime so that double-patching
    is correctly tested.
    """
    try:
        from pylons.templating import render_mako as render
    except ImportError:
        from pylons.templating import render

    return render
