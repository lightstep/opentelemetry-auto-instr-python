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

from .web.app import CustomDefaultHandler
from .utils import TornadoTestCase

from oteltrace import config
from oteltrace.constants import SAMPLING_PRIORITY_KEY, ORIGIN_KEY, ANALYTICS_SAMPLE_RATE_KEY
from oteltrace.ext import http


class TestTornadoWeb(TornadoTestCase):
    """
    Ensure that Tornado web handlers are properly traced.
    """
    def test_success_handler(self, query_string=''):
        # it should trace a handler that returns 200
        if query_string:
            fqs = '?' + query_string
        else:
            fqs = ''
        response = self.fetch('/success/' + fqs)
        assert 200 == response.code

        traces = self.tracer.writer.pop_traces()
        assert 1 == len(traces)
        assert 1 == len(traces[0])

        request_span = traces[0][0]
        assert 'tornado-web' == request_span.service
        assert 'tornado.request' == request_span.name
        assert 'http' == request_span.span_type
        assert 'tests.contrib.tornado.web.app.SuccessHandler' == request_span.resource
        assert 'GET' == request_span.get_tag('http.method')
        assert '200' == request_span.get_tag('http.status_code')
        assert self.get_url('/success/') == request_span.get_tag(http.URL)
        if config.tornado.trace_query_string:
            assert query_string == request_span.get_tag(http.QUERY_STRING)
        else:
            assert http.QUERY_STRING not in request_span.meta
        assert 0 == request_span.error

    def test_success_handler_query_string(self):
        self.test_success_handler('foo=bar')

    def test_success_handler_query_string_trace(self):
        with self.override_http_config('tornado', dict(trace_query_string=True)):
            self.test_success_handler('foo=bar')

    def test_nested_handler(self):
        # it should trace a handler that calls the tracer.trace() method
        # using the automatic Context retrieval
        response = self.fetch('/nested/')
        assert 200 == response.code
        traces = self.tracer.writer.pop_traces()
        assert 1 == len(traces)
        assert 2 == len(traces[0])
        # check request span
        request_span = traces[0][0]
        assert 'tornado-web' == request_span.service
        assert 'tornado.request' == request_span.name
        assert 'http' == request_span.span_type
        assert 'tests.contrib.tornado.web.app.NestedHandler' == request_span.resource
        assert 'GET' == request_span.get_tag('http.method')
        assert '200' == request_span.get_tag('http.status_code')
        assert self.get_url('/nested/') == request_span.get_tag(http.URL)
        assert 0 == request_span.error
        # check nested span
        nested_span = traces[0][1]
        assert 'tornado-web' == nested_span.service
        assert 'tornado.sleep' == nested_span.name
        assert 0 == nested_span.error
        # check durations because of the yield sleep
        assert request_span.duration >= 0.05
        assert nested_span.duration >= 0.05

    def test_exception_handler(self):
        # it should trace a handler that raises an exception
        response = self.fetch('/exception/')
        assert 500 == response.code

        traces = self.tracer.writer.pop_traces()
        assert 1 == len(traces)
        assert 1 == len(traces[0])

        request_span = traces[0][0]
        assert 'tornado-web' == request_span.service
        assert 'tornado.request' == request_span.name
        assert 'http' == request_span.span_type
        assert 'tests.contrib.tornado.web.app.ExceptionHandler' == request_span.resource
        assert 'GET' == request_span.get_tag('http.method')
        assert '500' == request_span.get_tag('http.status_code')
        assert self.get_url('/exception/') == request_span.get_tag(http.URL)
        assert 1 == request_span.error
        assert 'Ouch!' == request_span.get_tag('error.msg')
        assert 'Exception: Ouch!' in request_span.get_tag('error.stack')

    def test_http_exception_handler(self):
        # it should trace a handler that raises a Tornado HTTPError
        response = self.fetch('/http_exception/')
        assert 501 == response.code

        traces = self.tracer.writer.pop_traces()
        assert 1 == len(traces)
        assert 1 == len(traces[0])

        request_span = traces[0][0]
        assert 'tornado-web' == request_span.service
        assert 'tornado.request' == request_span.name
        assert 'http' == request_span.span_type
        assert 'tests.contrib.tornado.web.app.HTTPExceptionHandler' == request_span.resource
        assert 'GET' == request_span.get_tag('http.method')
        assert '501' == request_span.get_tag('http.status_code')
        assert self.get_url('/http_exception/') == request_span.get_tag(http.URL)
        assert 1 == request_span.error
        assert 'HTTP 501: Not Implemented (unavailable)' == request_span.get_tag('error.msg')
        assert 'HTTP 501: Not Implemented (unavailable)' in request_span.get_tag('error.stack')

    def test_http_exception_500_handler(self):
        # it should trace a handler that raises a Tornado HTTPError
        response = self.fetch('/http_exception_500/')
        assert 500 == response.code

        traces = self.tracer.writer.pop_traces()
        assert 1 == len(traces)
        assert 1 == len(traces[0])

        request_span = traces[0][0]
        assert 'tornado-web' == request_span.service
        assert 'tornado.request' == request_span.name
        assert 'http' == request_span.span_type
        assert 'tests.contrib.tornado.web.app.HTTPException500Handler' == request_span.resource
        assert 'GET' == request_span.get_tag('http.method')
        assert '500' == request_span.get_tag('http.status_code')
        assert self.get_url('/http_exception_500/') == request_span.get_tag(http.URL)
        assert 1 == request_span.error
        assert 'HTTP 500: Server Error (server error)' == request_span.get_tag('error.msg')
        assert 'HTTP 500: Server Error (server error)' in request_span.get_tag('error.stack')

    def test_sync_success_handler(self):
        # it should trace a synchronous handler that returns 200
        response = self.fetch('/sync_success/')
        assert 200 == response.code

        traces = self.tracer.writer.pop_traces()
        assert 1 == len(traces)
        assert 1 == len(traces[0])

        request_span = traces[0][0]
        assert 'tornado-web' == request_span.service
        assert 'tornado.request' == request_span.name
        assert 'http' == request_span.span_type
        assert 'tests.contrib.tornado.web.app.SyncSuccessHandler' == request_span.resource
        assert 'GET' == request_span.get_tag('http.method')
        assert '200' == request_span.get_tag('http.status_code')
        assert self.get_url('/sync_success/') == request_span.get_tag(http.URL)
        assert 0 == request_span.error

    def test_sync_exception_handler(self):
        # it should trace a handler that raises an exception
        response = self.fetch('/sync_exception/')
        assert 500 == response.code

        traces = self.tracer.writer.pop_traces()
        assert 1 == len(traces)
        assert 1 == len(traces[0])

        request_span = traces[0][0]
        assert 'tornado-web' == request_span.service
        assert 'tornado.request' == request_span.name
        assert 'http' == request_span.span_type
        assert 'tests.contrib.tornado.web.app.SyncExceptionHandler' == request_span.resource
        assert 'GET' == request_span.get_tag('http.method')
        assert '500' == request_span.get_tag('http.status_code')
        assert self.get_url('/sync_exception/') == request_span.get_tag(http.URL)
        assert 1 == request_span.error
        assert 'Ouch!' == request_span.get_tag('error.msg')
        assert 'Exception: Ouch!' in request_span.get_tag('error.stack')

    def test_404_handler(self):
        # it should trace 404
        response = self.fetch('/does_not_exist/')
        assert 404 == response.code

        traces = self.tracer.writer.pop_traces()
        assert 1 == len(traces)
        assert 1 == len(traces[0])

        request_span = traces[0][0]
        assert 'tornado-web' == request_span.service
        assert 'tornado.request' == request_span.name
        assert 'http' == request_span.span_type
        assert 'tornado.web.ErrorHandler' == request_span.resource
        assert 'GET' == request_span.get_tag('http.method')
        assert '404' == request_span.get_tag('http.status_code')
        assert self.get_url('/does_not_exist/') == request_span.get_tag(http.URL)
        assert 0 == request_span.error

    def test_redirect_handler(self):
        # it should trace the built-in RedirectHandler
        response = self.fetch('/redirect/')
        assert 200 == response.code

        # we trace two different calls: the RedirectHandler and the SuccessHandler
        traces = self.tracer.writer.pop_traces()
        assert 2 == len(traces)
        assert 1 == len(traces[0])
        assert 1 == len(traces[1])

        redirect_span = traces[0][0]
        assert 'tornado-web' == redirect_span.service
        assert 'tornado.request' == redirect_span.name
        assert 'http' == redirect_span.span_type
        assert 'tornado.web.RedirectHandler' == redirect_span.resource
        assert 'GET' == redirect_span.get_tag('http.method')
        assert '301' == redirect_span.get_tag('http.status_code')
        assert self.get_url('/redirect/') == redirect_span.get_tag(http.URL)
        assert 0 == redirect_span.error

        success_span = traces[1][0]
        assert 'tornado-web' == success_span.service
        assert 'tornado.request' == success_span.name
        assert 'http' == success_span.span_type
        assert 'tests.contrib.tornado.web.app.SuccessHandler' == success_span.resource
        assert 'GET' == success_span.get_tag('http.method')
        assert '200' == success_span.get_tag('http.status_code')
        assert self.get_url('/success/') == success_span.get_tag(http.URL)
        assert 0 == success_span.error

    def test_static_handler(self):
        # it should trace the access to static files
        response = self.fetch('/statics/empty.txt')
        assert 200 == response.code
        assert 'Static file\n' == response.body.decode('utf-8')

        traces = self.tracer.writer.pop_traces()
        assert 1 == len(traces)
        assert 1 == len(traces[0])

        request_span = traces[0][0]
        assert 'tornado-web' == request_span.service
        assert 'tornado.request' == request_span.name
        assert 'http' == request_span.span_type
        assert 'tornado.web.StaticFileHandler' == request_span.resource
        assert 'GET' == request_span.get_tag('http.method')
        assert '200' == request_span.get_tag('http.status_code')
        assert self.get_url('/statics/empty.txt') == request_span.get_tag(http.URL)
        assert 0 == request_span.error

    def test_propagation(self):
        # it should trace a handler that returns 200 with a propagated context
        headers = {
            'x-datadog-trace-id': '1234',
            'x-datadog-parent-id': '4567',
            'x-datadog-sampling-priority': '2'
        }
        response = self.fetch('/success/', headers=headers)
        assert 200 == response.code

        traces = self.tracer.writer.pop_traces()
        assert 1 == len(traces)
        assert 1 == len(traces[0])

        request_span = traces[0][0]

        # simple sanity check on the span
        assert 'tornado.request' == request_span.name
        assert '200' == request_span.get_tag('http.status_code')
        assert self.get_url('/success/') == request_span.get_tag(http.URL)
        assert 0 == request_span.error

        # check propagation
        assert 1234 == request_span.trace_id
        assert 4567 == request_span.parent_id
        assert 2 == request_span.get_metric(SAMPLING_PRIORITY_KEY)


class TestTornadoWebAnalyticsDefault(TornadoTestCase):
    """
    Ensure that Tornado web handlers generate APM events with default settings
    """
    def test_analytics_global_on_integration_default(self):
        """
        When making a request
            When an integration trace search is not event sample rate is not set and globally trace search is enabled
                We expect the root span to have the appropriate tag
        """
        with self.override_global_config(dict(analytics_enabled=True)):
            # it should trace a handler that returns 200
            response = self.fetch('/success/')
            self.assertEqual(200, response.code)

            self.assert_structure(
                dict(name='tornado.request', metrics={ANALYTICS_SAMPLE_RATE_KEY: 1.0}),
            )

    def test_analytics_global_off_integration_default(self):
        """
        When making a request
            When an integration trace search is not set and sample rate is set and globally trace search is disabled
                We expect the root span to not include tag
        """
        with self.override_global_config(dict(analytics_enabled=False)):
            # it should trace a handler that returns 200
            response = self.fetch('/success/')
            self.assertEqual(200, response.code)

            root = self.get_root_span()
            self.assertIsNone(root.get_metric(ANALYTICS_SAMPLE_RATE_KEY))


class TestTornadoWebAnalyticsOn(TornadoTestCase):
    """
    Ensure that Tornado web handlers generate APM events with default settings
    """
    def get_settings(self):
        # distributed_tracing needs to be disabled manually
        return {
            'opentelemetry_trace': {
                'analytics_enabled': True,
                'analytics_sample_rate': 0.5,
            },
        }

    def test_analytics_global_on_integration_on(self):
        """
        When making a request
            When an integration trace search is enabled and sample rate is set and globally trace search is enabled
                We expect the root span to have the appropriate tag
        """
        with self.override_global_config(dict(analytics_enabled=True)):
            # it should trace a handler that returns 200
            response = self.fetch('/success/')
            self.assertEqual(200, response.code)

            self.assert_structure(
                dict(name='tornado.request', metrics={ANALYTICS_SAMPLE_RATE_KEY: 0.5}),
            )

    def test_analytics_global_off_integration_on(self):
        """
        When making a request
            When an integration trace search is enabled and sample rate is set and globally trace search is disabled
                We expect the root span to have the appropriate tag
        """
        with self.override_global_config(dict(analytics_enabled=False)):
            # it should trace a handler that returns 200
            response = self.fetch('/success/')
            self.assertEqual(200, response.code)

            self.assert_structure(
                dict(name='tornado.request', metrics={ANALYTICS_SAMPLE_RATE_KEY: 0.5}),
            )


class TestTornadoWebAnalyticsNoRate(TornadoTestCase):
    """
    Ensure that Tornado web handlers generate APM events with default settings
    """
    def get_settings(self):
        # distributed_tracing needs to be disabled manually
        return {
            'opentelemetry_trace': {
                'analytics_enabled': True,
            },
        }

    def test_analytics_global_on_integration_on(self):
        """
        When making a request
            When an integration trace search is enabled and sample rate is set and globally trace search is enabled
                We expect the root span to have the appropriate tag
        """
        with self.override_global_config(dict(analytics_enabled=True)):
            # it should trace a handler that returns 200
            response = self.fetch('/success/')
            self.assertEqual(200, response.code)

            self.assert_structure(
                dict(name='tornado.request', metrics={ANALYTICS_SAMPLE_RATE_KEY: 1.0}),
            )


class TestNoPropagationTornadoWeb(TornadoTestCase):
    """
    Ensure that Tornado web handlers are properly traced and are ignoring propagated HTTP headers when disabled.
    """
    def get_settings(self):
        # distributed_tracing needs to be disabled manually
        return {
            'opentelemetry_trace': {
                'distributed_tracing': False,
            },
        }

    def test_no_propagation(self):
        # it should not propagate the HTTP context
        headers = {
            'x-datadog-trace-id': '1234',
            'x-datadog-parent-id': '4567',
            'x-datadog-sampling-priority': '2',
            'x-datadog-origin': 'synthetics',
        }
        response = self.fetch('/success/', headers=headers)
        assert 200 == response.code

        traces = self.tracer.writer.pop_traces()
        assert 1 == len(traces)
        assert 1 == len(traces[0])

        request_span = traces[0][0]

        # simple sanity check on the span
        assert 'tornado.request' == request_span.name
        assert '200' == request_span.get_tag('http.status_code')
        assert self.get_url('/success/') == request_span.get_tag(http.URL)
        assert 0 == request_span.error

        # check non-propagation
        assert request_span.trace_id != 1234
        assert request_span.parent_id != 4567
        assert request_span.get_metric(SAMPLING_PRIORITY_KEY) != 2
        assert request_span.get_tag(ORIGIN_KEY) != 'synthetics'


class TestCustomTornadoWeb(TornadoTestCase):
    """
    Ensure that Tornado web handlers are properly traced when using
    a custom default handler.
    """
    def get_settings(self):
        return {
            'default_handler_class': CustomDefaultHandler,
            'default_handler_args': dict(status_code=400),
        }

    def test_custom_default_handler(self):
        # it should trace any call that uses a custom default handler
        response = self.fetch('/custom_handler/')
        assert 400 == response.code

        traces = self.tracer.writer.pop_traces()
        assert 1 == len(traces)
        assert 1 == len(traces[0])

        request_span = traces[0][0]
        assert 'tornado-web' == request_span.service
        assert 'tornado.request' == request_span.name
        assert 'http' == request_span.span_type
        assert 'tests.contrib.tornado.web.app.CustomDefaultHandler' == request_span.resource
        assert 'GET' == request_span.get_tag('http.method')
        assert '400' == request_span.get_tag('http.status_code')
        assert self.get_url('/custom_handler/') == request_span.get_tag(http.URL)
        assert 0 == request_span.error
