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

import asyncio
import aiohttp_jinja2

from aiohttp.test_utils import unittest_run_loop

from oteltrace.pin import Pin
from oteltrace.contrib.aiohttp.patch import patch, unpatch

from .utils import TraceTestCase
from .app.web import set_filesystem_loader, set_package_loader


class TestTraceTemplate(TraceTestCase):
    """
    Ensures that the aiohttp_jinja2 library is properly traced.
    """
    def enable_tracing(self):
        patch()
        Pin.override(aiohttp_jinja2, tracer=self.tracer)

    def disable_tracing(self):
        unpatch()

    @unittest_run_loop
    @asyncio.coroutine
    def test_template_rendering(self):
        # it should trace a template rendering
        request = yield from self.client.request('GET', '/template/')
        assert 200 == request.status
        text = yield from request.text()
        assert 'OK' == text
        # the trace is created
        traces = self.tracer.writer.pop_traces()
        assert 1 == len(traces)
        assert 1 == len(traces[0])
        span = traces[0][0]
        # with the right fields
        assert 'aiohttp.template' == span.name
        assert 'template' == span.span_type
        assert '/template.jinja2' == span.get_tag('aiohttp.template')
        assert 0 == span.error

    @unittest_run_loop
    @asyncio.coroutine
    def test_template_rendering_filesystem(self):
        # it should trace a template rendering with a FileSystemLoader
        set_filesystem_loader(self.app)
        request = yield from self.client.request('GET', '/template/')
        assert 200 == request.status
        text = yield from request.text()
        assert 'OK' == text
        # the trace is created
        traces = self.tracer.writer.pop_traces()
        assert 1 == len(traces)
        assert 1 == len(traces[0])
        span = traces[0][0]
        # with the right fields
        assert 'aiohttp.template' == span.name
        assert 'template' == span.span_type
        assert '/template.jinja2' == span.get_tag('aiohttp.template')
        assert 0 == span.error

    @unittest_run_loop
    @asyncio.coroutine
    def test_template_rendering_package(self):
        # it should trace a template rendering with a PackageLoader
        set_package_loader(self.app)
        request = yield from self.client.request('GET', '/template/')
        assert 200 == request.status
        text = yield from request.text()
        assert 'OK' == text
        # the trace is created
        traces = self.tracer.writer.pop_traces()
        assert 1 == len(traces)
        assert 1 == len(traces[0])
        span = traces[0][0]
        # with the right fields
        assert 'aiohttp.template' == span.name
        assert 'template' == span.span_type
        assert 'templates/template.jinja2' == span.get_tag('aiohttp.template')
        assert 0 == span.error

    @unittest_run_loop
    @asyncio.coroutine
    def test_template_decorator(self):
        # it should trace a template rendering
        request = yield from self.client.request('GET', '/template_decorator/')
        assert 200 == request.status
        text = yield from request.text()
        assert 'OK' == text
        # the trace is created
        traces = self.tracer.writer.pop_traces()
        assert 1 == len(traces)
        assert 1 == len(traces[0])
        span = traces[0][0]
        # with the right fields
        assert 'aiohttp.template' == span.name
        assert 'template' == span.span_type
        assert '/template.jinja2' == span.get_tag('aiohttp.template')
        assert 0 == span.error

    @unittest_run_loop
    @asyncio.coroutine
    def test_template_error(self):
        # it should trace a template rendering
        request = yield from self.client.request('GET', '/template_error/')
        assert 500 == request.status
        yield from request.text()
        # the trace is created
        traces = self.tracer.writer.pop_traces()
        assert 1 == len(traces)
        assert 1 == len(traces[0])
        span = traces[0][0]
        # with the right fields
        assert 'aiohttp.template' == span.name
        assert 'template' == span.span_type
        assert '/error.jinja2' == span.get_tag('aiohttp.template')
        assert 1 == span.error
        assert 'division by zero' == span.get_tag('error.msg')
        assert 'ZeroDivisionError: division by zero' in span.get_tag('error.stack')
