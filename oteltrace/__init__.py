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

import sys

import pkg_resources

from .monkey import patch, patch_all
from .pin import Pin
from .span import Span
from .tracer import Tracer
from .settings import config


try:
    __version__ = pkg_resources.get_distribution(__name__).version
except pkg_resources.DistributionNotFound:
    # package is not installed
    __version__ = None


# a global tracer instance with integration settings
tracer = Tracer()

__all__ = [
    'patch',
    'patch_all',
    'Pin',
    'Span',
    'tracer',
    'Tracer',
    'config',
]


_ORIGINAL_EXCEPTHOOK = sys.excepthook


def _excepthook(type, value, traceback):
    tracer.global_excepthook(type, value, traceback)
    if _ORIGINAL_EXCEPTHOOK:
        return _ORIGINAL_EXCEPTHOOK(type, value, traceback)


def install_excepthook():
    """Install a hook that intercepts unhandled exception and send metrics about them."""
    global _ORIGINAL_EXCEPTHOOK
    _ORIGINAL_EXCEPTHOOK = sys.excepthook
    sys.excepthook = _excepthook


def uninstall_excepthook():
    """Uninstall the global tracer except hook."""
    sys.excepthook = _ORIGINAL_EXCEPTHOOK
