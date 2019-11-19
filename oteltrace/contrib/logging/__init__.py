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
OpenTelemetry APM traces can be integrated with Logs by first having the tracing
library patch the standard library ``logging`` module and updating the log
formatter used by an application. This feature enables you to inject the current
trace information into a log entry.

Before the trace information can be injected into logs, the formatter has to be
updated to include ``otel.trace_id`` and ``otel.span_id`` attributes from the log
record. The integration with Logs occurs as long as the log entry includes
``otel.trace_id=%(otel.trace_id)s`` and ``otel.span_id=%(otel.span_id)s``.

oteltrace-run
-----------

When using ``oteltrace-run``, enable patching by setting the environment variable
``OTEL_LOGS_INJECTION=true``. The logger by default will have a format that
includes trace information::

    import logging
    from oteltrace import tracer

    log = logging.getLogger()
    log.level = logging.INFO


    @tracer.wrap()
    def hello():
        log.info('Hello, World!')

    hello()

Manual Instrumentation
----------------------

If you prefer to instrument manually, patch the logging library then update the
log formatter as in the following example::

    from oteltrace import patch_all; patch_all(logging=True)
    import logging
    from oteltrace import tracer

    FORMAT = ('%(asctime)s %(levelname)s [%(name)s] [%(filename)s:%(lineno)d] '
              '[otel.trace_id=%(otel.trace_id)s otel.span_id=%(otel.span_id)s] '
              '- %(message)s')
    logging.basicConfig(format=FORMAT)
    log = logging.getLogger()
    log.level = logging.INFO


    @tracer.wrap()
    def hello():
        log.info('Hello, World!')

    hello()
"""

from ...utils.importlib import require_modules


required_modules = ['logging']

with require_modules(required_modules) as missing_modules:
    if not missing_modules:
        from .patch import patch, unpatch

        __all__ = ['patch', 'unpatch']
