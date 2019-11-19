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

"""Instrument mysql to report MySQL queries.

``patch_all`` will automatically patch your mysql connection to make it work.
::
    # Make sure to import mysql.connector and not the 'connect' function,
    # otherwise you won't have access to the patched version
    from oteltrace import Pin, patch
    import mysql.connector

    # If not patched yet, you can patch mysql specifically
    patch(mysql=True)

    # This will report a span with the default settings
    conn = mysql.connector.connect(user="alice", password="b0b", host="localhost", port=3306, database="test")
    cursor = conn.cursor()
    cursor.execute("SELECT 6*7 AS the_answer;")

    # Use a pin to specify metadata related to this connection
    Pin.override(conn, service='mysql-users')

Only the default full-Python integration works. The binary C connector,
provided by _mysql_connector, is not supported yet.

Help on mysql.connector can be found on:
https://dev.mysql.com/doc/connector-python/en/
"""
from ...utils.importlib import require_modules

# check `mysql-connector` availability
required_modules = ['mysql.connector']

with require_modules(required_modules) as missing_modules:
    if not missing_modules:
        from .patch import patch
        from .tracers import get_traced_mysql_connection

        __all__ = ['get_traced_mysql_connection', 'patch']
