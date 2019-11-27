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

"""
The pylons trace middleware will track request timings. To
install the middleware, prepare your WSGI application and do
the following::

    from pylons.wsgiapp import PylonsApp

    from oteltrace import tracer
    from oteltrace.contrib.pylons import PylonsTraceMiddleware

    app = PylonsApp(...)

    traced_app = PylonsTraceMiddleware(app, tracer, service='my-pylons-app')

Then you can define your routes and views as usual.
"""

from ...utils.importlib import require_modules


required_modules = ['pylons.wsgiapp']

with require_modules(required_modules) as missing_modules:
    if not missing_modules:
        from .middleware import PylonsTraceMiddleware
        from .patch import patch, unpatch

        __all__ = [
            'patch',
            'unpatch',
            'PylonsTraceMiddleware',
        ]
