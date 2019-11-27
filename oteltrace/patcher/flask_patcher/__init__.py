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
The Flask__ integration will add tracing to all requests to your Flask
application.

This integration will track the entire Flask lifecycle including user-defined
endpoints, hooks,
signals, and templating rendering.

To configure tracing manually::

    from oteltrace import patch_all
    patch_all()

    from flask import Flask

    app = Flask(__name__)


    @app.route('/')
    def index():
        return 'hello world'


    if __name__ == '__main__':
        app.run()


You may also enable Flask tracing automatically via oteltrace-run::

    oteltrace-run python app.py


Configuration
~~~~~~~~~~~~~

.. py:data:: oteltrace.config.flask['distributed_tracing_enabled']

   Whether to parse distributed tracing headers from requests received by
   your Flask app.

   Default: ``True``

.. py:data:: oteltrace.config.flask['analytics_enabled']

   Whether to generate APM events for Flask in Trace Search & Analytics.

   Can also be enabled with the ``OTEL_FLASK_ANALYTICS_ENABLED`` environment
   variable.

   Default: ``None``

.. py:data:: oteltrace.config.flask['service_name']

   The service name reported for your Flask app.

   Can also be configured via the ``OPENTELEMETRY_SERVICE_NAME`` environment
   variable.

   Default: ``'flask'``

.. py:data:: oteltrace.config.flask['collect_view_args']

   Whether to add request tags for view function argument values.

   Default: ``True``

.. py:data:: oteltrace.config.flask['template_default_name']

   The default template name to use when one does not exist.

   Default: ``<memory>``

.. py:data:: oteltrace.config.flask['trace_signals']

   Whether to trace Flask signals (``before_request``, ``after_request``, etc).

   Default: ``True``

.. py:data:: oteltrace.config.flask['extra_error_codes']

   A list of response codes that should get marked as errors.

   *5xx codes are always considered an error.*

   Default: ``[]``


Example::

    from oteltrace import config

    # Enable distributed tracing
    config.flask['distributed_tracing_enabled'] = True

    # Override service name
    config.flask['service_name'] = 'custom-service-name'

    # Report 401, and 403 responses as errors
    config.flask['extra_error_codes'] = [401, 403]

.. __: http://flask.pocoo.org/
"""

from ...utils.importlib import require_modules


required_modules = ['flask']

with require_modules(required_modules) as missing_modules:
    if not missing_modules:
        # DEV: We do this so we can
        # `@mock.patch('oteltrace.contrib.flask._patch.<func>')` in tests
        # from . import flask_patcher as _patch
        from .middleware import TraceMiddleware

        # patch = _patch.patch
        # unpatch = _patch.unpatch

        # __all__ = ['TraceMiddleware', 'patch', 'unpatch']
        __all__ = ['TraceMiddleware']
