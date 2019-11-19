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

import mock
from unittest import TestCase

from oteltrace.span import Span
from oteltrace.context import Context
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
from oteltrace.api_otel_exporter import APIOtel


class MockSpan(mock.Mock):
    pass


class TestAPIOtelExporter(TestCase):
    def test_init(self):
        exporter = mock.Mock()
        api = APIOtel(exporter=exporter)
        self.assertIs(api._exporter, exporter)

    def test_send_traces(self):
        def return_same(span):
            return span

        exporter = InMemorySpanExporter()
        api = APIOtel(exporter=exporter)
        # we don't care about _span_to_otel_span() here
        api._span_to_otel_span = return_same

        traces = (
            (MockSpan(),),
            (MockSpan(), MockSpan()),
            (MockSpan(), MockSpan(), MockSpan()),
        )

        api.send_traces(traces)

        # flat traces to 1 dimension tuple
        traces_tuple = tuple([item for sublist in traces for item in sublist])

        self.assertEqual(traces_tuple, exporter.get_finished_spans())

    def test__span_to_otel_span(self):
        api = APIOtel(exporter=None)

        trace_id = 0x32452526
        span_id = 0x29025326
        parent_id = 0x592153109

        start_time = 683647322
        end_time = start_time + 50

        ctx = Context()
        span = Span(
            tracer=None,
            name='test_span',
            trace_id=trace_id,
            span_id=span_id,
            parent_id=parent_id,
            context=ctx,
            start=start_time,
            resource='foo_resource',
            service='foo_service',
            span_type='foo_span',
        )

        span.finish(finish_time=end_time)

        span.set_tag('out.host', 'opentelemetry.io')
        span.set_tag('out.port', 443)
        span.set_tag('creator_name', 'mauricio.vasquez')

        otel_span = api._span_to_otel_span(span)

        self.assertEqual(span.name, otel_span.name)

        self.assertEqual(span.trace_id, otel_span.context.trace_id)
        self.assertEqual(span.span_id, otel_span.context.span_id)

        self.assertEqual(span.parent_id, otel_span.parent.span_id)
        self.assertEqual(span.trace_id, otel_span.parent.trace_id)

        self.assertEqual(start_time * 10 ** 9, otel_span.start_time)
        self.assertEqual(end_time * 10 ** 9, otel_span.end_time)

        self.assertEqual(span.service, otel_span.attributes['service.name'])
        self.assertEqual(span.resource, otel_span.attributes['resource.name'])
        self.assertEqual(span.span_type, otel_span.attributes['component'])

        self.assertEqual(span.get_tag('out.host'),
                         otel_span.attributes['peer.hostname'])
        self.assertEqual(span.get_tag('out.port'),
                         otel_span.attributes['peer.port'])

        self.assertEqual(span.get_tag('creator_name'),
                         otel_span.attributes['creator_name'])

        # test parent None

        span = Span(
            tracer=None,
            name='test_span',
            trace_id=trace_id,
            span_id=span_id,
            parent_id=None,
            context=ctx,
            start=start_time,
        )

        span.finish(finish_time=end_time)

        otel_span = api._span_to_otel_span(span)

        self.assertIsNone(otel_span.parent)
