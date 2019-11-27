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

"""Instrument rediscluster to report Redis Cluster queries.

``patch_all`` will automatically patch your Redis Cluster client to make it work.
::

    from oteltrace import Pin, patch
    import rediscluster

    # If not patched yet, you can patch redis specifically
    patch(rediscluster=True)

    # This will report a span with the default settings
    client = rediscluster.StrictRedisCluster(startup_nodes=[{'host':'localhost', 'port':'7000'}])
    client.get('my-key')

    # Use a pin to specify metadata related to this client
    Pin.override(client, service='redis-queue')
"""

from ...utils.importlib import require_modules

required_modules = ['rediscluster', 'rediscluster.client']

with require_modules(required_modules) as missing_modules:
    if not missing_modules:
        from .patch import patch

        __all__ = ['patch']
