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
The molten web framework is automatically traced by ``oteltrace`` when calling ``patch``::

    from molten import App, Route
    from oteltrace import patch_all; patch_all(molten=True)

    def hello(name: str, age: int) -> str:
        return f'Hello {age} year old named {name}!'
    app = App(routes=[Route('/hello/{name}/{age}', hello)])


You may also enable molten tracing automatically via ``oteltrace-run``::

    oteltrace-run python app.py


Configuration
~~~~~~~~~~~~~

.. py:data:: oteltrace.config.molten['distributed_tracing']

   Whether to parse distributed tracing headers from requests received by your Molten app.

   Default: ``True``

.. py:data:: oteltrace.config.molten['analytics_enabled']

   Whether to generate APM events in Trace Search & Analytics.

   Can also be enabled with the ``OTEL_MOLTEN_ANALYTICS_ENABLED`` environment variable.

   Default: ``None``

.. py:data:: oteltrace.config.molten['service_name']

   The service name reported for your Molten app.

   Can also be configured via the ``OTEL_MOLTEN_SERVICE_NAME`` environment variable.

   Default: ``'molten'``
"""
from ...utils.importlib import require_modules

required_modules = ['molten']

with require_modules(required_modules) as missing_modules:
    if not missing_modules:
        from . import patch as _patch

        patch = _patch.patch
        unpatch = _patch.unpatch

        __all__ = ['patch', 'unpatch']
