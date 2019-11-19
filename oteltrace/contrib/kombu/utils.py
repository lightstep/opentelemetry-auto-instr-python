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

"""
Some utils used by the dogtrace kombu integration
"""
from ...ext import kombu as kombux, net

PUBLISH_BODY_IDX = 0
PUBLISH_ROUTING_KEY = 6
PUBLISH_EXCHANGE_IDX = 9

HEADER_POS = 4


def extract_conn_tags(connection):
    """ Transform kombu conn info into dogtrace metas """
    try:
        host, port = connection.host.split(':')
        return {
            net.TARGET_HOST: host,
            net.TARGET_PORT: port,
            kombux.VHOST: connection.virtual_host,
        }
    except AttributeError:
        # Unlikely that we don't have .host or .virtual_host but let's not die over it
        return {}


def get_exchange_from_args(args):
    """Extract the exchange

    The publish method extracts the name and hands that off to _publish (what we patch)
    """

    return args[PUBLISH_EXCHANGE_IDX]


def get_routing_key_from_args(args):
    """Extract the routing key"""

    name = args[PUBLISH_ROUTING_KEY]
    return name


def get_body_length_from_args(args):
    """Extract the length of the body"""

    length = len(args[PUBLISH_BODY_IDX])
    return length
