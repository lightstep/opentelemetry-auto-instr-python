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

"""Instrument Elasticsearch to report Elasticsearch queries.

``patch_all`` will automatically patch your Elasticsearch instance to make it work.
::

    from oteltrace import Pin, patch
    from elasticsearch import Elasticsearch

    # If not patched yet, you can patch elasticsearch specifically
    patch(elasticsearch=True)

    # This will report spans with the default instrumentation
    es = Elasticsearch(port=ELASTICSEARCH_CONFIG['port'])
    # Example of instrumented query
    es.indices.create(index='books', ignore=400)

    # Use a pin to specify metadata related to this client
    es = Elasticsearch(port=ELASTICSEARCH_CONFIG['port'])
    Pin.override(es.transport, service='elasticsearch-videos')
    es.indices.create(index='videos', ignore=400)
"""
from ...utils.importlib import require_modules

# DEV: We only require one of these modules to be available
required_modules = ['elasticsearch', 'elasticsearch1', 'elasticsearch2', 'elasticsearch5']

with require_modules(required_modules) as missing_modules:
    # We were able to find at least one of the required modules
    if set(missing_modules) != set(required_modules):
        from .transport import get_traced_transport
        from .patch import patch

        __all__ = ['get_traced_transport', 'patch']
