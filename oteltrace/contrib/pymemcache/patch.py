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

import pymemcache

from oteltrace.ext import memcached as memcachedx
from oteltrace.pin import Pin, _OTEL_PIN_NAME, _OTEL_PIN_PROXY_NAME
from .client import WrappedClient

_Client = pymemcache.client.base.Client


def patch():
    if getattr(pymemcache.client, '_opentelemetry_patch', False):
        return

    setattr(pymemcache.client, '_opentelemetry_patch', True)
    setattr(pymemcache.client.base, 'Client', WrappedClient)

    # Create a global pin with default configuration for our pymemcache clients
    Pin(
        app=memcachedx.SERVICE, service=memcachedx.SERVICE, app_type=memcachedx.TYPE
    ).onto(pymemcache)


def unpatch():
    """Remove pymemcache tracing"""
    if not getattr(pymemcache.client, '_opentelemetry_patch', False):
        return
    setattr(pymemcache.client, '_opentelemetry_patch', False)
    setattr(pymemcache.client.base, 'Client', _Client)

    # Remove any pins that may exist on the pymemcache reference
    setattr(pymemcache, _OTEL_PIN_NAME, None)
    setattr(pymemcache, _OTEL_PIN_PROXY_NAME, None)
