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

"""Instrument mysqlclient / MySQL-python to report MySQL queries.

``patch_all`` will automatically patch your mysql connection to make it work.
::
    # Make sure to import MySQLdb and not the 'connect' function,
    # otherwise you won't have access to the patched version
    from oteltrace import Pin, patch
    import MySQLdb

    # If not patched yet, you can patch mysqldb specifically
    patch(mysqldb=True)

    # This will report a span with the default settings
    conn = MySQLdb.connect(user="alice", passwd="b0b", host="localhost", port=3306, db="test")
    cursor = conn.cursor()
    cursor.execute("SELECT 6*7 AS the_answer;")

    # Use a pin to specify metadata related to this connection
    Pin.override(conn, service='mysql-users')

This package works for mysqlclient or MySQL-python. Only the default
full-Python integration works. The binary C connector provided by
_mysql is not yet supported.

Help on mysqlclient can be found on:
https://mysqlclient.readthedocs.io/
"""
from ...utils.importlib import require_modules

required_modules = ['MySQLdb']

with require_modules(required_modules) as missing_modules:
    if not missing_modules:
        from .patch import patch

        __all__ = ['patch']
