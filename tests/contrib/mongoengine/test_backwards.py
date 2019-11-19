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
ensure old interfaces exist and won't break things.
"""
import mongoengine

from tests.test_tracer import get_dummy_tracer
from tests.contrib import config


class Singer(mongoengine.Document):
    first_name = mongoengine.StringField(max_length=50)
    last_name = mongoengine.StringField(max_length=50)


def test_less_than_v04():
    # interface from < v0.4
    from oteltrace.contrib.mongoengine import trace_mongoengine
    tracer = get_dummy_tracer()

    connect = trace_mongoengine(tracer, service='my-mongo-db', patch=False)
    connect(port=config.MONGO_CONFIG['port'])

    lc = Singer()
    lc.first_name = 'leonard'
    lc.last_name = 'cohen'
    lc.save()
