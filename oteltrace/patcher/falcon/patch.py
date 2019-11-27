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
import falcon

from oteltrace import tracer

from .middleware import TraceMiddleware
from ...utils.formats import asbool, get_env


def patch():
    """
    Patch falcon.API to include contrib.falcon.TraceMiddleware
    by default
    """
    if getattr(falcon, '_opentelemetry_patch', False):
        return

    setattr(falcon, '_opentelemetry_patch', True)
    wrapt.wrap_function_wrapper('falcon', 'API.__init__', traced_init)


def traced_init(wrapped, instance, args, kwargs):
    mw = kwargs.pop('middleware', [])
    service = os.environ.get('OPENTELEMETRY_SERVICE_NAME') or 'falcon'
    distributed_tracing = asbool(get_env('falcon', 'distributed_tracing', True))

    mw.insert(0, TraceMiddleware(tracer, service, distributed_tracing))
    kwargs['middleware'] = mw

    wrapped(*args, **kwargs)
