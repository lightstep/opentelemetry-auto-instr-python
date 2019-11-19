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

"""Instrument pylibmc to report Memcached queries.

``patch_all`` will automatically patch your pylibmc client to make it work.
::

    # Be sure to import pylibmc and not pylibmc.Client directly,
    # otherwise you won't have access to the patched version
    from oteltrace import Pin, patch
    import pylibmc

    # If not patched yet, you can patch pylibmc specifically
    patch(pylibmc=True)

    # One client instrumented with default configuration
    client = pylibmc.Client(["localhost:11211"]
    client.set("key1", "value1")

    # Use a pin to specify metadata related to this client
    Pin.override(client, service="memcached-sessions")
"""

from ...utils.importlib import require_modules

required_modules = ['pylibmc']

with require_modules(required_modules) as missing_modules:
    if not missing_modules:
        from .client import TracedClient
        from .patch import patch

        __all__ = ['TracedClient', 'patch']
