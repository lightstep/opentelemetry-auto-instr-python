from unittest import TestCase
from tests.test_tracer import get_dummy_tracer

from oteltrace.propagation.http import (
    HTTPPropagator,
    HTTP_HEADER_TRACE_ID,
    HTTP_HEADER_PARENT_ID,
    HTTP_HEADER_SAMPLING_PRIORITY,
    HTTP_HEADER_ORIGIN,
)


class TestHttpPropagation(TestCase):
    """
    Tests related to the ``Context`` class that hosts the trace for the
    current execution flow.
    """

    def test_inject(self):
        tracer = get_dummy_tracer()

        with tracer.trace('global_root_span') as span:
            span.context.sampling_priority = 2
            span.context._dd_origin = 'synthetics'
            headers = {}
            propagator = HTTPPropagator()
            propagator.inject(span.context, headers)

            assert int(headers[HTTP_HEADER_TRACE_ID]) == span.trace_id
            assert int(headers[HTTP_HEADER_PARENT_ID]) == span.span_id
            assert (
                int(headers[HTTP_HEADER_SAMPLING_PRIORITY]) ==
                span.context.sampling_priority
            )
            assert (
                headers[HTTP_HEADER_ORIGIN] ==
                span.context._dd_origin
            )

    def test_extract(self):
        tracer = get_dummy_tracer()

        headers = {
            'x-opentelemetry-trace-id': '1234',
            'x-opentelemetry-parent-id': '5678',
            'x-opentelemetry-sampling-priority': '1',
            'x-opentelemetry-origin': 'synthetics',
        }

        propagator = HTTPPropagator()
        context = propagator.extract(headers)
        tracer.context_provider.activate(context)

        with tracer.trace('local_root_span') as span:
            assert span.trace_id == 1234
            assert span.parent_id == 5678
            assert span.context.sampling_priority == 1
            assert span.context._dd_origin == 'synthetics'

    def test_WSGI_extract(self):
        """Ensure we support the WSGI formatted headers as well."""
        tracer = get_dummy_tracer()

        headers = {
            'HTTP_X_OPENTELEMETRY_TRACE_ID': '1234',
            'HTTP_X_OPENTELEMETRY_PARENT_ID': '5678',
            'HTTP_X_OPENTELEMETRY_SAMPLING_PRIORITY': '1',
            'HTTP_X_OPENTELEMETRY_ORIGIN': 'synthetics',
        }

        propagator = HTTPPropagator()
        context = propagator.extract(headers)
        tracer.context_provider.activate(context)

        with tracer.trace('local_root_span') as span:
            assert span.trace_id == 1234
            assert span.parent_id == 5678
            assert span.context.sampling_priority == 1
            assert span.context._dd_origin == 'synthetics'
