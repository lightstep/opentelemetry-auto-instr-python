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

from oteltrace.contrib.pymysql import get_traced_pymysql_connection
from tests.test_tracer import get_dummy_tracer
from tests.contrib import config


def test_pre_v4():
    tracer = get_dummy_tracer()
    MySQL = get_traced_pymysql_connection(tracer, service='my-mysql-server')
    conn = MySQL(**config.MYSQL_CONFIG)
    cursor = conn.cursor()
    cursor.execute('SELECT 1')
    assert cursor.fetchone()[0] == 1
