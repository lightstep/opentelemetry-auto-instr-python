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

"""To trace requests from a Pyramid application, trace your application
config::


    from pyramid.config import Configurator
    from oteltrace.contrib.pyramid import trace_pyramid

    settings = {
        'opentelemetry_trace_service' : 'my-web-app-name',
    }

    config = Configurator(settings=settings)
    trace_pyramid(config)

    # use your config as normal.
    config.add_route('index', '/')

Available settings are:

* ``opentelemetry_trace_service``: change the `pyramid` service name
* ``opentelemetry_trace_enabled``: sets if the Tracer is enabled or not
* ``opentelemetry_distributed_tracing``: set it to ``False`` to disable Distributed Tracing
* ``opentelemetry_analytics_enabled``: set it to ``True`` to enable generating APM events for Trace Search & Analytics

If you use the ``pyramid.tweens`` settings value to set the tweens for your
application, you need to add ``oteltrace.contrib.pyramid:trace_tween_factory``
explicitly to the list. For example::

    settings = {
        'opentelemetry_trace_service' : 'my-web-app-name',
        'pyramid.tweens', 'your_tween_no_1\\nyour_tween_no_2\\noteltrace.contrib.pyramid:trace_tween_factory',
    }

    config = Configurator(settings=settings)
    trace_pyramid(config)

    # use your config as normal.
    config.add_route('index', '/')

"""

from ...utils.importlib import require_modules


required_modules = ['pyramid']

with require_modules(required_modules) as missing_modules:
    if not missing_modules:
        from .trace import trace_pyramid, trace_tween_factory, includeme
        from .patch import patch

        __all__ = [
            'patch',
            'trace_pyramid',
            'trace_tween_factory',
            'includeme',
        ]
