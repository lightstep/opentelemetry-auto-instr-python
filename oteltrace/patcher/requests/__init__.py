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
The ``requests`` integration traces all HTTP calls to internal or external services.
Auto instrumentation is available using the ``patch`` function that **must be called
before** importing the ``requests`` library. The following is an example::

    from oteltrace import patch
    patch(requests=True)

    import requests
    requests.get("https://www.datadoghq.com")

If you would prefer finer grained control, use a ``TracedSession`` object as you would a
``requests.Session``::

    from oteltrace.contrib.requests import TracedSession

    session = TracedSession()
    session.get("https://www.datadoghq.com")

The library can be configured globally and per instance, using the Configuration API::

    from oteltrace import config

    # disable distributed tracing globally
    config.requests['distributed_tracing'] = False

    # enable trace analytics globally
    config.requests['analytics_enabled'] = True

    # change the service name/distributed tracing only for this session
    session = Session()
    cfg = config.get_from(session)
    cfg['service_name'] = 'auth-api'
    cfg['analytics_enabled'] = True

:ref:`Headers tracing <http-headers-tracing>` is supported for this integration.
"""
from ...utils.importlib import require_modules


required_modules = ['requests']

with require_modules(required_modules) as missing_modules:
    if not missing_modules:
        from .patch import patch, unpatch
        from .session import TracedSession

        __all__ = [
            'patch',
            'unpatch',
            'TracedSession',
        ]
