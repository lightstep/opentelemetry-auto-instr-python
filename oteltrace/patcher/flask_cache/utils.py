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

# project
from ...ext import net
from ..redis.util import _extract_conn_tags as extract_redis_tags
from ..pylibmc.addrs import parse_addresses


def _resource_from_cache_prefix(resource, cache):
    """
    Combine the resource name with the cache prefix (if any)
    """
    if getattr(cache, 'key_prefix', None):
        name = '{} {}'.format(resource, cache.key_prefix)
    else:
        name = resource

    # enforce lowercase to make the output nicer to read
    return name.lower()


def _extract_conn_tags(client):
    """
    For the given client extracts connection tags
    """
    tags = {}

    if hasattr(client, 'servers'):
        # Memcached backend supports an address pool
        if isinstance(client.servers, list) and len(client.servers) > 0:
            # use the first address of the pool as a host because
            # the code doesn't expose more information
            contact_point = client.servers[0].address
            tags[net.TARGET_HOST] = contact_point[0]
            tags[net.TARGET_PORT] = contact_point[1]
    elif hasattr(client, 'connection_pool'):
        # Redis main connection
        redis_tags = extract_redis_tags(client.connection_pool.connection_kwargs)
        tags.update(**redis_tags)
    elif hasattr(client, 'addresses'):
        # pylibmc
        # FIXME[matt] should we memoize this?
        addrs = parse_addresses(client.addresses)
        if addrs:
            _, host, port, _ = addrs[0]
            tags[net.TARGET_PORT] = port
            tags[net.TARGET_HOST] = host
    return tags
