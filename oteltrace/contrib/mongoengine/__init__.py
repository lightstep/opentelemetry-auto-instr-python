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

"""Instrument mongoengine to report MongoDB queries.

``patch_all`` will automatically patch your mongoengine connect method to make it work.
::

    from oteltrace import Pin, patch
    import mongoengine

    # If not patched yet, you can patch mongoengine specifically
    patch(mongoengine=True)

    # At that point, mongoengine is instrumented with the default settings
    mongoengine.connect('db', alias='default')

    # Use a pin to specify metadata related to this client
    client = mongoengine.connect('db', alias='master')
    Pin.override(client, service="mongo-master")
"""

from ...utils.importlib import require_modules


required_modules = ['mongoengine']

with require_modules(required_modules) as missing_modules:
    if not missing_modules:
        from .patch import patch, trace_mongoengine

        __all__ = ['patch', 'trace_mongoengine']
