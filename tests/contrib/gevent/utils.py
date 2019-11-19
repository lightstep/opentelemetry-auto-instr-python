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

import gevent

from functools import wraps


_NOT_ERROR = gevent.hub.Hub.NOT_ERROR


def silence_errors(f):
    """
    Test decorator for gevent that silences all errors when
    a greenlet raises an exception.
    """
    @wraps(f)
    def wrapper(*args, **kwargs):
        gevent.hub.Hub.NOT_ERROR = (Exception,)
        f(*args, **kwargs)
        gevent.hub.Hub.NOT_ERROR = _NOT_ERROR
    return wrapper
