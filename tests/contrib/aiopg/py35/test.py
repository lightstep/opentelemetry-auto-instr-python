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

# stdlib
import asyncio

# 3p
import aiopg

# project
from oteltrace.contrib.aiopg.patch import patch, unpatch
from oteltrace import Pin

# testing
from tests.contrib.config import POSTGRES_CONFIG
from tests.contrib.asyncio.utils import AsyncioTestCase, mark_asyncio


TEST_PORT = str(POSTGRES_CONFIG['port'])


class TestPsycopgPatch(AsyncioTestCase):
    # default service
    TEST_SERVICE = 'postgres'

    def setUp(self):
        super().setUp()
        self._conn = None
        patch()

    def tearDown(self):
        super().tearDown()
        if self._conn and not self._conn.closed:
            self._conn.close()

        unpatch()

    @asyncio.coroutine
    def _get_conn_and_tracer(self):
        conn = self._conn = yield from aiopg.connect(**POSTGRES_CONFIG)
        Pin.get_from(conn).clone(tracer=self.tracer).onto(conn)

        return conn, self.tracer

    async def _test_cursor_ctx_manager(self):
        conn, tracer = await self._get_conn_and_tracer()
        cur = await conn.cursor()
        t = type(cur)

        async with conn.cursor() as cur:
            assert t == type(cur), '%s != %s' % (t, type(cur))
            await cur.execute(query='select \'blah\'')
            rows = await cur.fetchall()
            assert len(rows) == 1
            assert rows[0][0] == 'blah'

        spans = tracer.writer.pop()
        assert len(spans) == 1
        span = spans[0]
        assert span.name == 'postgres.query'

    @mark_asyncio
    def test_cursor_ctx_manager(self):
        # ensure cursors work with context managers
        # https://github.com/opentelemetry/otel-trace-py/issues/228
        yield from self._test_cursor_ctx_manager()
