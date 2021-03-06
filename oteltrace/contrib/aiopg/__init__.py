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
Instrument aiopg to report a span for each executed Postgres queries::

    from oteltrace import Pin, patch
    import aiopg

    # If not patched yet, you can patch aiopg specifically
    patch(aiopg=True)

    # This will report a span with the default settings
    async with aiopg.connect(DSN) as db:
        with (await db.cursor()) as cursor:
            await cursor.execute("SELECT * FROM users WHERE id = 1")

    # Use a pin to specify metadata related to this connection
    Pin.override(db, service='postgres-users')
"""
from ...utils.importlib import require_modules


required_modules = ['aiopg']

with require_modules(required_modules) as missing_modules:
    if not missing_modules:
        from .patch import patch

        __all__ = ['patch']
