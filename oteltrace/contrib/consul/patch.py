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

import consul

from oteltrace.vendor.wrapt import wrap_function_wrapper as _w

from oteltrace import config
from ...constants import ANALYTICS_SAMPLE_RATE_KEY
from ...ext import consul as consulx
from ...pin import Pin
from ...utils.wrappers import unwrap as _u


_KV_FUNCS = ['put', 'get', 'delete']


def patch():
    if getattr(consul, '__opentelemetry_patch', False):
        return
    setattr(consul, '__opentelemetry_patch', True)

    pin = Pin(service=consulx.SERVICE, app=consulx.APP, app_type=consulx.APP_TYPE)
    pin.onto(consul.Consul.KV)

    for f_name in _KV_FUNCS:
        _w('consul', 'Consul.KV.%s' % f_name, wrap_function(f_name))


def unpatch():
    if not getattr(consul, '__opentelemetry_patch', False):
        return
    setattr(consul, '__opentelemetry_patch', False)

    for f_name in _KV_FUNCS:
        _u(consul.Consul.KV, f_name)


def wrap_function(name):
    def trace_func(wrapped, instance, args, kwargs):
        pin = Pin.get_from(instance)
        if not pin or not pin.enabled():
            return wrapped(*args, **kwargs)

        # Only patch the syncronous implementation
        if not isinstance(instance.agent.http, consul.std.HTTPClient):
            return wrapped(*args, **kwargs)

        path = kwargs.get('key') or args[0]
        resource = name.upper()

        with pin.tracer.trace(consulx.CMD, service=pin.service, resource=resource) as span:
            rate = config.consul.get_analytics_sample_rate()
            if rate is not None:
                span.set_tag(ANALYTICS_SAMPLE_RATE_KEY, rate)
            span.set_tag(consulx.KEY, path)
            span.set_tag(consulx.CMD, resource)
            return wrapped(*args, **kwargs)

    return trace_func
