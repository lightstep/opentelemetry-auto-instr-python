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

import bottle
import oteltrace
import webtest

from unittest import TestCase
from tests.test_tracer import get_dummy_tracer

from oteltrace import compat


SERVICE = 'bottle-app'


class TraceBottleTest(TestCase):
    """
    Ensures that Bottle is properly traced.
    """
    def setUp(self):
        # provide a dummy tracer
        self.tracer = get_dummy_tracer()
        self._original_tracer = oteltrace.tracer
        oteltrace.tracer = self.tracer
        # provide a Bottle app
        self.app = bottle.Bottle()

    def tearDown(self):
        # restore the tracer
        oteltrace.tracer = self._original_tracer

    def _trace_app(self, tracer=None):
        self.app = webtest.TestApp(self.app)

    def test_200(self):
        # setup our test app
        @self.app.route('/hi/<name>')
        def hi(name):
            return 'hi %s' % name
        self._trace_app(self.tracer)

        # make a request
        resp = self.app.get('/hi/dougie')
        assert resp.status_int == 200
        assert compat.to_unicode(resp.body) == u'hi dougie'
        # validate it's traced
        spans = self.tracer.writer.pop()
        assert len(spans) == 1
        s = spans[0]
        assert s.name == 'bottle.request'
        assert s.service == 'bottle-app'
        assert s.resource == 'GET /hi/<name>'
        assert s.get_tag('http.status_code') == '200'
        assert s.get_tag('http.method') == 'GET'

        services = self.tracer.writer.pop_services()
        assert services == {}

    def test_500(self):
        @self.app.route('/hi')
        def hi():
            raise Exception('oh no')
        self._trace_app(self.tracer)

        # make a request
        try:
            resp = self.app.get('/hi')
            assert resp.status_int == 500
        except Exception:
            pass

        spans = self.tracer.writer.pop()
        assert len(spans) == 1
        s = spans[0]
        assert s.name == 'bottle.request'
        assert s.service == 'bottle-app'
        assert s.resource == 'GET /hi'
        assert s.get_tag('http.status_code') == '500'
        assert s.get_tag('http.method') == 'GET'

    def test_bottle_global_tracer(self):
        # without providing a Tracer instance, it should work
        @self.app.route('/home/')
        def home():
            return 'Hello world'
        self._trace_app()

        # make a request
        resp = self.app.get('/home/')
        assert resp.status_int == 200
        # validate it's traced
        spans = self.tracer.writer.pop()
        assert len(spans) == 1
        s = spans[0]
        assert s.name == 'bottle.request'
        assert s.service == 'bottle-app'
        assert s.resource == 'GET /home/'
        assert s.get_tag('http.status_code') == '200'
        assert s.get_tag('http.method') == 'GET'
