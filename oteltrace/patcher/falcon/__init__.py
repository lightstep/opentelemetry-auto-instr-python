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
To trace the falcon web framework, install the trace middleware::

    import falcon
    from oteltrace import tracer
    from oteltrace.contrib.falcon import TraceMiddleware

    mw = TraceMiddleware(tracer, 'my-falcon-app')
    falcon.API(middleware=[mw])

You can also use the autopatching functionality::

    import falcon
    from oteltrace import tracer, patch

    patch(falcon=True)

    app = falcon.API()

To disable distributed tracing when using autopatching, set the
``OPENTELEMETRY_FALCON_DISTRIBUTED_TRACING`` environment variable to ``False``.

To enable generating APM events for Trace Search & Analytics, set the
``OTEL_FALCON_ANALYTICS_ENABLED`` environment variable to ``True``.

**Supported span hooks**

The following is a list of available tracer hooks that can be used to intercept
and modify spans created by this integration.

- ``request``
    - Called before the response has been finished
    - ``def on_falcon_request(span, request, response)``


Example::

    import falcon
    from oteltrace import config, patch_all
    patch_all()

    app = falcon.API()

    @config.falcon.hooks.on('request')
    def on_falcon_request(span, request, response):
        span.set_tag('my.custom', 'tag')

:ref:`Headers tracing <http-headers-tracing>` is supported for this integration.
"""
from ...utils.importlib import require_modules

required_modules = ['falcon']

with require_modules(required_modules) as missing_modules:
    if not missing_modules:
        from .middleware import TraceMiddleware
        from .patch import patch

        __all__ = ['TraceMiddleware', 'patch']
