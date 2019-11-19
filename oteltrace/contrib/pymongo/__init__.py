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

"""Instrument pymongo to report MongoDB queries.

The pymongo integration works by wrapping pymongo's MongoClient to trace
network calls. Pymongo 3.0 and greater are the currently supported versions.
``patch_all`` will automatically patch your MongoClient instance to make it work.
::
    # Be sure to import pymongo and not pymongo.MongoClient directly,
    # otherwise you won't have access to the patched version
    from oteltrace import Pin, patch
    import pymongo

    # If not patched yet, you can patch pymongo specifically
    patch(pymongo=True)

    # At that point, pymongo is instrumented with the default settings
    client = pymongo.MongoClient()
    # Example of instrumented query
    db = client["test-db"]
    db.teams.find({"name": "Toronto Maple Leafs"})

    # Use a pin to specify metadata related to this client
    client = pymongo.MongoClient()
    pin = Pin.override(client, service="mongo-master")
"""
from ...utils.importlib import require_modules


required_modules = ['pymongo']

with require_modules(required_modules) as missing_modules:
    if not missing_modules:
        from .client import trace_mongo_client
        from .patch import patch
        __all__ = ['trace_mongo_client', 'patch']
