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

"""Instrument Consul to trace KV queries.

Only supports tracing for the syncronous client.

``patch_all`` will automatically patch your Consul client to make it work.
::

    from oteltrace import Pin, patch
    import consul

    # If not patched yet, you can patch consul specifically
    patch(consul=True)

    # This will report a span with the default settings
    client = consul.Consul(host="127.0.0.1", port=8500)
    client.get("my-key")

    # Use a pin to specify metadata related to this client
    Pin.override(client, service='consul-kv')
"""

from ...utils.importlib import require_modules

required_modules = ['consul']

with require_modules(required_modules) as missing_modules:
    if not missing_modules:
        from .patch import patch, unpatch
        __all__ = ['patch', 'unpatch']
