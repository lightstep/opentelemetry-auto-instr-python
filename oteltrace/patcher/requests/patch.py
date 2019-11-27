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

import requests

from oteltrace.vendor.wrapt import wrap_function_wrapper as _w

from oteltrace import config

from ...pin import Pin
from ...utils.formats import asbool, get_env
from ...utils.wrappers import unwrap as _u
from .legacy import _distributed_tracing, _distributed_tracing_setter
from .constants import DEFAULT_SERVICE
from .connection import _wrap_send
from ...ext import AppTypes

# requests default settings
config._add('requests', {
    'service_name': get_env('requests', 'service_name', DEFAULT_SERVICE),
    'distributed_tracing': asbool(get_env('requests', 'distributed_tracing', True)),
    'split_by_domain': asbool(get_env('requests', 'split_by_domain', False)),
})


def patch():
    """Activate http calls tracing"""
    if getattr(requests, '__opentelemetry_patch', False):
        return
    setattr(requests, '__opentelemetry_patch', True)

    _w('requests', 'Session.send', _wrap_send)
    Pin(
        service=config.requests['service_name'],
        app='requests',
        app_type=AppTypes.web,
        _config=config.requests,
    ).onto(requests.Session)

    # [Backward compatibility]: `session.distributed_tracing` should point and
    # update the `Pin` configuration instead. This block adds a property so that
    # old implementations work as expected
    fn = property(_distributed_tracing)
    fn = fn.setter(_distributed_tracing_setter)
    requests.Session.distributed_tracing = fn


def unpatch():
    """Disable traced sessions"""
    if not getattr(requests, '__opentelemetry_patch', False):
        return
    setattr(requests, '__opentelemetry_patch', False)

    _u(requests.Session, 'send')
