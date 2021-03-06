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
Tracing utilities for the psycopg potgres client library.
"""

# stdlib
import functools

from ...ext import db
from ...ext import net
from ...ext import sql
from ...utils.deprecation import deprecated

# 3p
from psycopg2.extensions import connection, cursor


@deprecated(message='Use patching instead (see the docs).', version='1.0.0')
def connection_factory(tracer, service='postgres'):
    """ Return a connection factory class that will can be used to trace
        postgres queries.

        >>> factory = connection_factor(my_tracer, service='my_db_service')
        >>> conn = pyscopg2.connect(..., connection_factory=factory)
    """

    return functools.partial(
        TracedConnection,
        opentelemetry_tracer=tracer,
        opentelemetry_service=service,
    )


class TracedCursor(cursor):
    """Wrapper around cursor creating one span per query"""

    def __init__(self, *args, **kwargs):
        self._opentelemetry_tracer = kwargs.pop('opentelemetry_tracer', None)
        self._opentelemetry_service = kwargs.pop('opentelemetry_service', None)
        self._opentelemetry_tags = kwargs.pop('opentelemetry_tags', None)
        super(TracedCursor, self).__init__(*args, **kwargs)

    def execute(self, query, vars=None):
        """ just wrap the cursor execution in a span """
        if not self._opentelemetry_tracer:
            return cursor.execute(self, query, vars)

        with self._opentelemetry_tracer.trace('postgres.query', service=self._opentelemetry_service) as s:
            if not s.sampled:
                return super(TracedCursor, self).execute(query, vars)

            s.resource = query
            s.span_type = sql.TYPE
            s.set_tags(self._opentelemetry_tags)
            try:
                return super(TracedCursor, self).execute(query, vars)
            finally:
                s.set_metric('db.rowcount', self.rowcount)

    def callproc(self, procname, vars=None):
        """ just wrap the execution in a span """
        return cursor.callproc(self, procname, vars)


class TracedConnection(connection):
    """Wrapper around psycopg2  for tracing"""

    def __init__(self, *args, **kwargs):

        self._opentelemetry_tracer = kwargs.pop('opentelemetry_tracer', None)
        self._opentelemetry_service = kwargs.pop('opentelemetry_service', None)

        super(TracedConnection, self).__init__(*args, **kwargs)

        # add metadata (from the connection, string, etc)
        dsn = sql.parse_pg_dsn(self.dsn)
        self._opentelemetry_tags = {
            net.TARGET_HOST: dsn.get('host'),
            net.TARGET_PORT: dsn.get('port'),
            db.NAME: dsn.get('dbname'),
            db.USER: dsn.get('user'),
            'db.application': dsn.get('application_name'),
        }

        self._opentelemetry_cursor_class = functools.partial(
            TracedCursor,
            opentelemetry_tracer=self._opentelemetry_tracer,
            opentelemetry_service=self._opentelemetry_service,
            opentelemetry_tags=self._opentelemetry_tags,
        )

    def cursor(self, *args, **kwargs):
        """ register our custom cursor factory """
        kwargs.setdefault('cursor_factory', self._opentelemetry_cursor_class)
        return super(TracedConnection, self).cursor(*args, **kwargs)
