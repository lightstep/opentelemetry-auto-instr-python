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

"""Instrument pymemcache to report memcached queries.

``patch_all`` will automatically patch the pymemcache ``Client``::

    from oteltrace import Pin, patch

    # If not patched yet, patch pymemcache specifically
    patch(pymemcache=True)

    # Import reference to Client AFTER patching
    import pymemcache
    from pymemcache.client.base import Client

    # Use a pin to specify metadata related all clients
    Pin.override(pymemcache, service='my-memcached-service')

    # This will report a span with the default settings
    client = Client(('localhost', 11211))
    client.set("my-key", "my-val")

    # Use a pin to specify metadata related to this particular client
    Pin.override(client, service='my-memcached-service')

Pymemcache ``HashClient`` will also be indirectly patched as it uses ``Client``
under the hood.
"""
from ...utils.importlib import require_modules


required_modules = ['pymemcache']

with require_modules(required_modules) as missing_modules:
    if not missing_modules:
        from .patch import patch, unpatch
        __all__ = [
            patch,
            unpatch,
        ]
