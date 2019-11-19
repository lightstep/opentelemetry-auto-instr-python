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

# 3p
import aiopg

# project
from oteltrace.contrib.aiopg.patch import patch, unpatch
from oteltrace import Pin

# testing
from tests.contrib.config import POSTGRES_CONFIG
from tests.contrib.asyncio.utils import AsyncioTestCase, mark_asyncio


TEST_PORT = str(POSTGRES_CONFIG['port'])


class AiopgTestCase(AsyncioTestCase):
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

    async def _get_conn_and_tracer(self):
        conn = self._conn = await aiopg.connect(**POSTGRES_CONFIG)
        Pin.get_from(conn).clone(tracer=self.tracer).onto(conn)

        return conn, self.tracer

    @mark_asyncio
    async def test_async_generator(self):
        conn, tracer = await self._get_conn_and_tracer()
        cursor = await conn.cursor()
        q = 'select \'foobarblah\''
        await cursor.execute(q)
        rows = []
        async for row in cursor:
            rows.append(row)

        assert rows == [('foobarblah',)]
        spans = tracer.writer.pop()
        assert len(spans) == 1
        span = spans[0]
        assert span.name == 'postgres.query'
