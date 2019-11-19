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

import json

from pyramid.httpexceptions import HTTPException
import pytest
import webtest

from oteltrace import compat
from oteltrace import config
from oteltrace.constants import ANALYTICS_SAMPLE_RATE_KEY
from oteltrace.contrib.pyramid.patch import insert_tween_if_needed
from oteltrace.ext import http

from .app import create_app

from ...base import BaseTracerTestCase


class PyramidBase(BaseTracerTestCase):
    """Base Pyramid test application"""
    def setUp(self):
        super(PyramidBase, self).setUp()
        self.create_app()

    def create_app(self, settings=None):
        # get default settings or use what is provided
        settings = settings or self.get_settings()
        # always set the dummy tracer as a default tracer
        settings.update({'opentelemetry_tracer': self.tracer})

        app, renderer = create_app(settings, self.instrument)
        self.app = webtest.TestApp(app)
        self.renderer = renderer

    def get_settings(self):
        return {}

    def override_settings(self, settings):
        self.create_app(settings)


class PyramidTestCase(PyramidBase):
    """Pyramid TestCase that includes tests for automatic instrumentation"""
    instrument = True

    def get_settings(self):
        return {
            'opentelemetry_trace_service': 'foobar',
        }

    def test_200(self, query_string=''):
        if query_string:
            fqs = '?' + query_string
        else:
            fqs = ''
        res = self.app.get('/' + fqs, status=200)
        assert b'idx' in res.body

        writer = self.tracer.writer
        spans = writer.pop()
        assert len(spans) == 1
        s = spans[0]
        assert s.service == 'foobar'
        assert s.resource == 'GET index'
        assert s.error == 0
        assert s.span_type == 'http'
        assert s.meta.get('http.method') == 'GET'
        assert s.meta.get('http.status_code') == '200'
        assert s.meta.get(http.URL) == 'http://localhost/'
        if config.pyramid.trace_query_string:
            assert s.meta.get(http.QUERY_STRING) == query_string
        else:
            assert http.QUERY_STRING not in s.meta
        assert s.meta.get('pyramid.route.name') == 'index'

        # ensure services are set correctly
        services = writer.pop_services()
        expected = {}
        assert services == expected

    def test_200_query_string(self):
        return self.test_200('foo=bar')

    def test_200_query_string_trace(self):
        with self.override_http_config('pyramid', dict(trace_query_string=True)):
            return self.test_200('foo=bar')

    def test_analytics_global_on_integration_default(self):
        """
        When making a request
            When an integration trace search is not event sample rate is not set and globally trace search is enabled
                We expect the root span to have the appropriate tag
        """
        with self.override_global_config(dict(analytics_enabled=True)):
            res = self.app.get('/', status=200)
            assert b'idx' in res.body

            self.assert_structure(
                dict(name='pyramid.request', metrics={ANALYTICS_SAMPLE_RATE_KEY: 1.0}),
            )

    def test_analytics_global_on_integration_on(self):
        """
        When making a request
            When an integration trace search is enabled and sample rate is set and globally trace search is enabled
                We expect the root span to have the appropriate tag
        """
        with self.override_global_config(dict(analytics_enabled=True)):
            self.override_settings(dict(opentelemetry_analytics_enabled=True, opentelemetry_analytics_sample_rate=0.5))
            res = self.app.get('/', status=200)
            assert b'idx' in res.body

            self.assert_structure(
                dict(name='pyramid.request', metrics={ANALYTICS_SAMPLE_RATE_KEY: 0.5}),
            )

    def test_analytics_global_off_integration_default(self):
        """
        When making a request
            When an integration trace search is not set and sample rate is set and globally trace search is disabled
                We expect the root span to not include tag
        """
        with self.override_global_config(dict(analytics_enabled=False)):
            res = self.app.get('/', status=200)
            assert b'idx' in res.body

            root = self.get_root_span()
            self.assertIsNone(root.get_metric(ANALYTICS_SAMPLE_RATE_KEY))

    def test_analytics_global_off_integration_on(self):
        """
        When making a request
            When an integration trace search is enabled and sample rate is set and globally trace search is disabled
                We expect the root span to have the appropriate tag
        """
        with self.override_global_config(dict(analytics_enabled=False)):
            self.override_settings(dict(opentelemetry_analytics_enabled=True, opentelemetry_analytics_sample_rate=0.5))
            res = self.app.get('/', status=200)
            assert b'idx' in res.body

            self.assert_structure(
                dict(name='pyramid.request', metrics={ANALYTICS_SAMPLE_RATE_KEY: 0.5}),
            )

    def test_404(self):
        self.app.get('/404', status=404)

        writer = self.tracer.writer
        spans = writer.pop()
        assert len(spans) == 1
        s = spans[0]
        assert s.service == 'foobar'
        assert s.resource == '404'
        assert s.error == 0
        assert s.span_type == 'http'
        assert s.meta.get('http.method') == 'GET'
        assert s.meta.get('http.status_code') == '404'
        assert s.meta.get(http.URL) == 'http://localhost/404'

    def test_302(self):
        self.app.get('/redirect', status=302)

        writer = self.tracer.writer
        spans = writer.pop()
        assert len(spans) == 1
        s = spans[0]
        assert s.service == 'foobar'
        assert s.resource == 'GET raise_redirect'
        assert s.error == 0
        assert s.span_type == 'http'
        assert s.meta.get('http.method') == 'GET'
        assert s.meta.get('http.status_code') == '302'
        assert s.meta.get(http.URL) == 'http://localhost/redirect'

    def test_204(self):
        self.app.get('/nocontent', status=204)

        writer = self.tracer.writer
        spans = writer.pop()
        assert len(spans) == 1
        s = spans[0]
        assert s.service == 'foobar'
        assert s.resource == 'GET raise_no_content'
        assert s.error == 0
        assert s.span_type == 'http'
        assert s.meta.get('http.method') == 'GET'
        assert s.meta.get('http.status_code') == '204'
        assert s.meta.get(http.URL) == 'http://localhost/nocontent'

    def test_exception(self):
        try:
            self.app.get('/exception', status=500)
        except ZeroDivisionError:
            pass

        writer = self.tracer.writer
        spans = writer.pop()
        assert len(spans) == 1
        s = spans[0]
        assert s.service == 'foobar'
        assert s.resource == 'GET exception'
        assert s.error == 1
        assert s.span_type == 'http'
        assert s.meta.get('http.method') == 'GET'
        assert s.meta.get('http.status_code') == '500'
        assert s.meta.get(http.URL) == 'http://localhost/exception'
        assert s.meta.get('pyramid.route.name') == 'exception'

    def test_500(self):
        self.app.get('/error', status=500)

        writer = self.tracer.writer
        spans = writer.pop()
        assert len(spans) == 1
        s = spans[0]
        assert s.service == 'foobar'
        assert s.resource == 'GET error'
        assert s.error == 1
        assert s.span_type == 'http'
        assert s.meta.get('http.method') == 'GET'
        assert s.meta.get('http.status_code') == '500'
        assert s.meta.get(http.URL) == 'http://localhost/error'
        assert s.meta.get('pyramid.route.name') == 'error'
        assert type(s.error) == int

    def test_json(self):
        res = self.app.get('/json', status=200)
        parsed = json.loads(compat.to_unicode(res.body))
        assert parsed == {'a': 1}

        writer = self.tracer.writer
        spans = writer.pop()
        assert len(spans) == 2
        spans_by_name = {s.name: s for s in spans}
        s = spans_by_name['pyramid.request']
        assert s.service == 'foobar'
        assert s.resource == 'GET json'
        assert s.error == 0
        assert s.span_type == 'http'
        assert s.meta.get('http.method') == 'GET'
        assert s.meta.get('http.status_code') == '200'
        assert s.meta.get(http.URL) == 'http://localhost/json'
        assert s.meta.get('pyramid.route.name') == 'json'

        s = spans_by_name['pyramid.render']
        assert s.service == 'foobar'
        assert s.error == 0
        assert s.span_type == 'template'

    def test_renderer(self):
        self.app.get('/renderer', status=200)
        assert self.renderer._received['request'] is not None

        self.renderer.assert_(foo='bar')
        writer = self.tracer.writer
        spans = writer.pop()
        assert len(spans) == 2
        spans_by_name = {s.name: s for s in spans}
        s = spans_by_name['pyramid.request']
        assert s.service == 'foobar'
        assert s.resource == 'GET renderer'
        assert s.error == 0
        assert s.span_type == 'http'
        assert s.meta.get('http.method') == 'GET'
        assert s.meta.get('http.status_code') == '200'
        assert s.meta.get(http.URL) == 'http://localhost/renderer'
        assert s.meta.get('pyramid.route.name') == 'renderer'

        s = spans_by_name['pyramid.render']
        assert s.service == 'foobar'
        assert s.error == 0
        assert s.span_type == 'template'

    def test_http_exception_response(self):
        with pytest.raises(HTTPException):
            self.app.get('/404/raise_exception', status=404)

        writer = self.tracer.writer
        spans = writer.pop()
        assert len(spans) == 1
        s = spans[0]
        assert s.service == 'foobar'
        assert s.resource == '404'
        assert s.error == 1
        assert s.span_type == 'http'
        assert s.meta.get('http.method') == 'GET'
        assert s.meta.get('http.status_code') == '404'
        assert s.meta.get(http.URL) == 'http://localhost/404/raise_exception'

    def test_insert_tween_if_needed_already_set(self):
        settings = {'pyramid.tweens': 'oteltrace.contrib.pyramid:trace_tween_factory'}
        insert_tween_if_needed(settings)
        assert settings['pyramid.tweens'] == 'oteltrace.contrib.pyramid:trace_tween_factory'

    def test_insert_tween_if_needed_none(self):
        settings = {'pyramid.tweens': ''}
        insert_tween_if_needed(settings)
        assert settings['pyramid.tweens'] == ''

    def test_insert_tween_if_needed_excview(self):
        settings = {'pyramid.tweens': 'pyramid.tweens.excview_tween_factory'}
        insert_tween_if_needed(settings)
        assert (
            settings['pyramid.tweens'] ==
            'oteltrace.contrib.pyramid:trace_tween_factory\npyramid.tweens.excview_tween_factory'
        )

    def test_insert_tween_if_needed_excview_and_other(self):
        settings = {'pyramid.tweens': 'a.first.tween\npyramid.tweens.excview_tween_factory\na.last.tween\n'}
        insert_tween_if_needed(settings)
        assert (
            settings['pyramid.tweens'] ==
            'a.first.tween\n'
            'oteltrace.contrib.pyramid:trace_tween_factory\n'
            'pyramid.tweens.excview_tween_factory\n'
            'a.last.tween\n')

    def test_insert_tween_if_needed_others(self):
        settings = {'pyramid.tweens': 'a.random.tween\nand.another.one'}
        insert_tween_if_needed(settings)
        assert (
            settings['pyramid.tweens'] ==
            'a.random.tween\nand.another.one\noteltrace.contrib.pyramid:trace_tween_factory'
        )

    def test_include_conflicts(self):
        # test that includes do not create conflicts
        self.override_settings({'pyramid.includes': 'tests.contrib.pyramid.test_pyramid'})
        self.app.get('/404', status=404)
        spans = self.tracer.writer.pop()
        assert len(spans) == 1
