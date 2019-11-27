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

import mongoengine

from .trace import WrappedConnect
from ...utils.deprecation import deprecated

# Original connect function
_connect = mongoengine.connect


def patch():
    setattr(mongoengine, 'connect', WrappedConnect(_connect))


def unpatch():
    setattr(mongoengine, 'connect', _connect)


@deprecated(message='Use patching instead (see the docs).', version='1.0.0')
def trace_mongoengine(*args, **kwargs):
    return _connect
