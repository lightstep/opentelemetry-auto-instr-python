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

import requests

from oteltrace.vendor.wrapt import wrap_function_wrapper as _w

from .connection import _wrap_send


class TracedSession(requests.Session):
    """TracedSession is a requests' Session that is already traced.
    You can use it if you want a finer grained control for your
    HTTP clients.
    """
    pass


# always patch our `TracedSession` when imported
_w(TracedSession, 'send', _wrap_send)
