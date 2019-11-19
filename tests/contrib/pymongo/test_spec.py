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
tests for parsing specs.
"""

from bson.son import SON

from oteltrace.contrib.pymongo.parse import parse_spec


def test_empty():
    cmd = parse_spec(SON([]))
    assert cmd is None


def test_create():
    cmd = parse_spec(SON([('create', 'foo')]))
    assert cmd.name == 'create'
    assert cmd.coll == 'foo'
    assert cmd.tags == {}
    assert cmd.metrics == {}


def test_insert():
    spec = SON([
        ('insert', 'bla'),
        ('ordered', True),
        ('documents', ['a', 'b']),
    ])
    cmd = parse_spec(spec)
    assert cmd.name == 'insert'
    assert cmd.coll == 'bla'
    assert cmd.tags == {'mongodb.ordered': True}
    assert cmd.metrics == {'mongodb.documents': 2}


def test_update():
    spec = SON([
        ('update', u'songs'),
        ('ordered', True),
        ('updates', [
            SON([
                ('q', {'artist': 'Neil'}),
                ('u', {'$set': {'artist': 'Shakey'}}),
                ('multi', True),
                ('upsert', False)
            ])
        ])
    ])
    cmd = parse_spec(spec)
    assert cmd.name == 'update'
    assert cmd.coll == 'songs'
    assert cmd.query == {'artist': 'Neil'}
