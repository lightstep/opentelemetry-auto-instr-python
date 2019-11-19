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

import os
from oteltrace.vendor import wrapt
import pylons.wsgiapp

from oteltrace import tracer, Pin

from .middleware import PylonsTraceMiddleware
from ...utils.formats import asbool, get_env
from ...utils.wrappers import unwrap as _u


def patch():
    """Instrument Pylons applications"""
    if getattr(pylons.wsgiapp, '_opentelemetry_patch', False):
        return

    setattr(pylons.wsgiapp, '_opentelemetry_patch', True)
    wrapt.wrap_function_wrapper('pylons.wsgiapp', 'PylonsApp.__init__', traced_init)


def unpatch():
    """Disable Pylons tracing"""
    if not getattr(pylons.wsgiapp, '__opentelemetry_patch', False):
        return
    setattr(pylons.wsgiapp, '__opentelemetry_patch', False)

    _u(pylons.wsgiapp.PylonsApp, '__init__')


def traced_init(wrapped, instance, args, kwargs):
    wrapped(*args, **kwargs)

    # set tracing options and create the TraceMiddleware
    service = os.environ.get('OPENTELEMETRY_SERVICE_NAME', 'pylons')
    distributed_tracing = asbool(get_env('pylons', 'distributed_tracing', True))
    Pin(service=service, tracer=tracer).onto(instance)
    traced_app = PylonsTraceMiddleware(instance, tracer, service=service, distributed_tracing=distributed_tracing)

    # re-order the middleware stack so that the first middleware is ours
    traced_app.app = instance.app
    instance.app = traced_app
