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
An integration test that uses a real Redis client
that we expect to be implicitly traced via `oteltrace-run`
"""

import redis

from oteltrace import Pin
from tests.contrib.config import REDIS_CONFIG
from tests.test_tracer import DummyWriter

if __name__ == '__main__':
    r = redis.Redis(port=REDIS_CONFIG['port'])
    pin = Pin.get_from(r)
    assert pin
    assert pin.app == 'redis'
    assert pin.service == 'redis'

    pin.tracer.writer = DummyWriter()
    r.flushall()
    spans = pin.tracer.writer.pop()

    assert len(spans) == 1
    assert spans[0].service == 'redis'
    assert spans[0].resource == 'FLUSHALL'

    long_cmd = 'mget %s' % ' '.join(map(str, range(1000)))
    us = r.execute_command(long_cmd)

    spans = pin.tracer.writer.pop()
    assert len(spans) == 1
    span = spans[0]
    assert span.service == 'redis'
    assert span.name == 'redis.command'
    assert span.span_type == 'redis'
    assert span.error == 0
    meta = {
        'out.host': u'localhost',
        'out.port': str(REDIS_CONFIG['port']),
        'out.redis_db': u'0',
    }
    for k, v in meta.items():
        assert span.get_tag(k) == v

    assert span.get_tag('redis.raw_command').startswith(u'mget 0 1 2 3')
    assert span.get_tag('redis.raw_command').endswith(u'...')

    print('Test success')
