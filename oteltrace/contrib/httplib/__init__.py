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
Patch the built-in ``httplib``/``http.client`` libraries to trace all HTTP calls.


Usage::

    # Patch all supported modules/functions
    from oteltrace import patch
    patch(httplib=True)

    # Python 2
    import httplib
    import urllib

    resp = urllib.urlopen('http://opentelemetry.io/')

    # Python 3
    import http.client
    import urllib.request

    resp = urllib.request.urlopen('http://opentelemetry.io/')

``httplib`` spans do not include a default service name. Before HTTP calls are
made, ensure a parent span has been started with a service name to be used for
spans generated from those calls::

    with tracer.trace('main', service='my-httplib-operation'):
        resp = urllib.request.urlopen('http://opentelemetry.io/')

:ref:`Headers tracing <http-headers-tracing>` is supported for this integration.
"""
from .patch import patch, unpatch
__all__ = ['patch', 'unpatch']
