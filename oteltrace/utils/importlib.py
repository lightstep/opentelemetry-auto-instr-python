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

from __future__ import absolute_import

from importlib import import_module


class require_modules(object):
    """Context manager to check the availability of required modules."""
    def __init__(self, modules):
        self._missing_modules = []
        for module in modules:
            try:
                import_module(module)
            except ImportError:
                self._missing_modules.append(module)

    def __enter__(self):
        return self._missing_modules

    def __exit__(self, exc_type, exc_value, traceback):
        return False


def func_name(f):
    """Return a human readable version of the function's name."""
    if hasattr(f, '__module__'):
        return '%s.%s' % (f.__module__, getattr(f, '__name__', f.__class__.__name__))
    return getattr(f, '__name__', f.__class__.__name__)


def module_name(instance):
    """Return the instance module name."""
    return instance.__class__.__module__.split('.')[0]
