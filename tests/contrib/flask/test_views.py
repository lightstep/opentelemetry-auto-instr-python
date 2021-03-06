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

from flask.views import MethodView, View

from oteltrace.compat import PY2
from oteltrace.ext import http

from . import BaseFlaskTestCase


base_exception_name = 'builtins.Exception'
if PY2:
    base_exception_name = 'exceptions.Exception'


class FlaskViewTestCase(BaseFlaskTestCase):
    def test_view_handler(self):
        """
        When using a flask.views.View
            We create spans as expected
        """
        class TestView(View):
            methods = ['GET']

            def dispatch_request(self, name):
                return 'Hello {}'.format(name)

        self.app.add_url_rule('/hello/<name>', view_func=TestView.as_view('hello'))

        res = self.client.get('/hello/flask')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data, b'Hello flask')

        spans = self.get_spans()

        req_span = self.find_span_by_name(spans, 'flask.request')
        handler_span = self.find_span_by_name(spans, 'tests.contrib.flask.test_views.hello')

        # flask.request
        self.assertEqual(req_span.error, 0)
        self.assertEqual(
            set(req_span.meta.keys()),
            set(['flask.endpoint', 'flask.url_rule', 'flask.version', 'flask.view_args.name',
                 'http.method', 'http.status_code', 'http.url', 'system.pid']),
        )
        self.assertEqual(req_span.get_tag('flask.endpoint'), 'hello')
        self.assertEqual(req_span.get_tag('flask.url_rule'), '/hello/<name>')
        self.assertEqual(req_span.get_tag('flask.view_args.name'), 'flask')
        self.assertEqual(req_span.get_tag('http.method'), 'GET')
        self.assertEqual(req_span.get_tag('http.status_code'), '200')
        self.assertEqual(req_span.get_tag(http.URL), 'http://localhost/hello/flask')

        # tests.contrib.flask.test_views.hello
        # DEV: We do not add any additional metadata to view spans
        self.assertEqual(handler_span.error, 0)
        self.assertEqual(handler_span.meta, dict())

    def test_view_handler_error(self):
        """
        When using a flask.views.View
            When it raises an exception
                We create spans as expected
        """
        class TestView(View):
            methods = ['GET']

            def dispatch_request(self, name):
                raise Exception('an error')

        self.app.add_url_rule('/hello/<name>', view_func=TestView.as_view('hello'))

        res = self.client.get('/hello/flask')
        self.assertEqual(res.status_code, 500)

        spans = self.get_spans()

        req_span = self.find_span_by_name(spans, 'flask.request')
        dispatch_span = self.find_span_by_name(spans, 'flask.dispatch_request')
        handler_span = self.find_span_by_name(spans, 'tests.contrib.flask.test_views.hello')

        # flask.request
        self.assertEqual(req_span.error, 1)
        self.assertEqual(
            set(req_span.meta.keys()),
            set(['flask.endpoint', 'flask.url_rule', 'flask.version', 'flask.view_args.name',
                 'http.method', 'http.status_code', 'http.url', 'system.pid']),
        )
        self.assertEqual(req_span.get_tag('flask.endpoint'), 'hello')
        self.assertEqual(req_span.get_tag('flask.url_rule'), '/hello/<name>')
        self.assertEqual(req_span.get_tag('flask.view_args.name'), 'flask')
        self.assertEqual(req_span.get_tag('http.method'), 'GET')
        self.assertEqual(req_span.get_tag('http.status_code'), '500')
        self.assertEqual(req_span.get_tag(http.URL), 'http://localhost/hello/flask')

        # flask.dispatch_request
        self.assertEqual(dispatch_span.error, 1)
        self.assertEqual(dispatch_span.get_tag('error.msg'), 'an error')
        self.assertTrue(dispatch_span.get_tag('error.stack').startswith('Traceback (most recent call last):'))
        self.assertEqual(dispatch_span.get_tag('error.type'), base_exception_name)

        # tests.contrib.flask.test_views.hello
        # DEV: We do not add any additional metadata to view spans
        self.assertEqual(handler_span.error, 1)
        self.assertEqual(handler_span.get_tag('error.msg'), 'an error')
        self.assertTrue(handler_span.get_tag('error.stack').startswith('Traceback (most recent call last):'))
        self.assertEqual(handler_span.get_tag('error.type'), base_exception_name)

    def test_method_view_handler(self):
        """
        When using a flask.views.MethodView
            We create spans as expected
        """
        class TestView(MethodView):
            def get(self, name):
                return 'Hello {}'.format(name)

        self.app.add_url_rule('/hello/<name>', view_func=TestView.as_view('hello'))

        res = self.client.get('/hello/flask')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data, b'Hello flask')

        spans = self.get_spans()

        req_span = self.find_span_by_name(spans, 'flask.request')
        handler_span = self.find_span_by_name(spans, 'tests.contrib.flask.test_views.hello')

        # flask.request
        self.assertEqual(req_span.error, 0)
        self.assertEqual(
            set(req_span.meta.keys()),
            set(['flask.endpoint', 'flask.url_rule', 'flask.version', 'flask.view_args.name',
                 'http.method', 'http.status_code', 'http.url', 'system.pid']),
        )
        self.assertEqual(req_span.get_tag('flask.endpoint'), 'hello')
        self.assertEqual(req_span.get_tag('flask.url_rule'), '/hello/<name>')
        self.assertEqual(req_span.get_tag('flask.view_args.name'), 'flask')
        self.assertEqual(req_span.get_tag('http.method'), 'GET')
        self.assertEqual(req_span.get_tag('http.status_code'), '200')
        self.assertEqual(req_span.get_tag(http.URL), 'http://localhost/hello/flask')

        # tests.contrib.flask.test_views.hello
        # DEV: We do not add any additional metadata to view spans
        self.assertEqual(handler_span.error, 0)
        self.assertEqual(handler_span.meta, dict())

    def test_method_view_handler_error(self):
        """
        When using a flask.views.View
            When it raises an exception
                We create spans as expected
        """
        class TestView(MethodView):
            def get(self, name):
                raise Exception('an error')

        self.app.add_url_rule('/hello/<name>', view_func=TestView.as_view('hello'))

        res = self.client.get('/hello/flask')
        self.assertEqual(res.status_code, 500)

        spans = self.get_spans()

        req_span = self.find_span_by_name(spans, 'flask.request')
        dispatch_span = self.find_span_by_name(spans, 'flask.dispatch_request')
        handler_span = self.find_span_by_name(spans, 'tests.contrib.flask.test_views.hello')

        # flask.request
        self.assertEqual(req_span.error, 1)
        self.assertEqual(
            set(req_span.meta.keys()),
            set(['flask.endpoint', 'flask.url_rule', 'flask.version', 'flask.view_args.name',
                 'http.method', 'http.status_code', 'http.url', 'system.pid']),
        )
        self.assertEqual(req_span.get_tag('flask.endpoint'), 'hello')
        self.assertEqual(req_span.get_tag('flask.url_rule'), '/hello/<name>')
        self.assertEqual(req_span.get_tag('flask.view_args.name'), 'flask')
        self.assertEqual(req_span.get_tag('http.method'), 'GET')
        self.assertEqual(req_span.get_tag('http.status_code'), '500')
        self.assertEqual(req_span.get_tag(http.URL), 'http://localhost/hello/flask')

        # flask.dispatch_request
        self.assertEqual(dispatch_span.error, 1)
        self.assertEqual(dispatch_span.get_tag('error.msg'), 'an error')
        self.assertTrue(dispatch_span.get_tag('error.stack').startswith('Traceback (most recent call last):'))
        self.assertEqual(dispatch_span.get_tag('error.type'), base_exception_name)

        # tests.contrib.flask.test_views.hello
        # DEV: We do not add any additional metadata to view spans
        self.assertEqual(handler_span.error, 1)
        self.assertEqual(handler_span.get_tag('error.msg'), 'an error')
        self.assertTrue(handler_span.get_tag('error.stack').startswith('Traceback (most recent call last):'))
        self.assertEqual(handler_span.get_tag('error.type'), base_exception_name)
