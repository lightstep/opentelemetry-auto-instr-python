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

from oteltrace.ext import AppTypes


# the type of the spans
TYPE = 'sql'
APP_TYPE = AppTypes.db

# tags
QUERY = 'sql.query'   # the query text
ROWS = 'sql.rows'     # number of rows returned by a query
DB = 'sql.db'         # the name of the database


def normalize_vendor(vendor):
    """ Return a canonical name for a type of database. """
    if not vendor:
        return 'db'  # should this ever happen?
    elif 'sqlite' in vendor:
        return 'sqlite'
    elif 'postgres' in vendor or vendor == 'psycopg2':
        return 'postgres'
    else:
        return vendor


def parse_pg_dsn(dsn):
    """
    Return a dictionary of the components of a postgres DSN.

    >>> parse_pg_dsn('user=dog port=1543 dbname=dogdata')
    {'user':'dog', 'port':'1543', 'dbname':'dogdata'}
    """
    # FIXME: replace by psycopg2.extensions.parse_dsn when available
    # https://github.com/psycopg/psycopg2/pull/321
    return {c.split('=')[0]: c.split('=')[1] for c in dsn.split() if '=' in c}
