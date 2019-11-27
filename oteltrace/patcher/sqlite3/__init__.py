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

"""Instrument sqlite3 to report SQLite queries.

``patch_all`` will automatically patch your sqlite3 connection to make it work.
::

    from oteltrace import Pin, patch
    import sqlite3

    # If not patched yet, you can patch sqlite3 specifically
    patch(sqlite3=True)

    # This will report a span with the default settings
    db = sqlite3.connect(":memory:")
    cursor = db.cursor()
    cursor.execute("select * from users where id = 1")

    # Use a pin to specify metadata related to this connection
    Pin.override(db, service='sqlite-users')
"""
from .connection import connection_factory
from .patch import patch

__all__ = ['connection_factory', 'patch']
