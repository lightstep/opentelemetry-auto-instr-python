from unittest import TestCase

from oteltrace.tracer import Tracer
from oteltrace.constants import FILTERS_KEY
from oteltrace.ext import http
from oteltrace.filters import FilterRequestsOnUrl
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
from oteltrace.api_otel_exporter import APIOtel


class TestWorkers(TestCase):
    """
    Ensures that a workers interacts correctly with the main thread. These are part
    of integration tests so real calls are triggered.
    """

    def setUp(self):
        """
        Create a tracer with running workers, while spying the ``_put()`` method to
        keep trace of triggered API calls.
        """
        self.exporter = InMemorySpanExporter()
        api = APIOtel(exporter=self.exporter)

        # create a new tracer
        self.tracer = Tracer()
        self.tracer.configure(api=api)
        # spy the send() method
        self.api = self.tracer.writer.api

    def tearDown(self):
        """
        Stop running worker
        """
        self._wait_thread_flush()

    def _wait_thread_flush(self):
        """
        Helper that waits for the thread flush
        """
        self.tracer.writer.stop()
        self.tracer.writer.join(None)

    def test_worker_single_trace(self):
        # create a trace block and send it using the transport system
        tracer = self.tracer
        tracer.trace('client.testing').finish()

        # one send is expected
        self._wait_thread_flush()

        spans = self.exporter.get_finished_spans()

        self.assertEqual(len(spans), 1)
        self.assertEqual(spans[0].name, 'client.testing')

    def test_worker_single_trace_multiple_spans(self):
        # make a single send() if a single trace with multiple spans is created before the flush
        tracer = self.tracer
        parent = tracer.trace('client.testing.parent')
        tracer.trace('client.testing.child').finish()
        parent.finish()

        # one send is expected
        self._wait_thread_flush()

        spans = self.exporter.get_finished_spans()

        self.assertEqual(len(spans), 2)
        self.assertEqual(spans[0].name, 'client.testing.parent')
        self.assertEqual(spans[1].name, 'client.testing.child')

    def test_worker_filter_request(self):
        self.tracer.configure(
            settings={FILTERS_KEY: [FilterRequestsOnUrl(r'http://example\.com/health')]},
            api=self.api,
        )

        span = self.tracer.trace('testing.filteredurl')
        span.set_tag(http.URL, 'http://example.com/health')
        span.finish()
        span = self.tracer.trace('testing.nonfilteredurl')
        span.set_tag(http.URL, 'http://example.com/api/resource')
        span.finish()
        self._wait_thread_flush()

        spans = self.exporter.get_finished_spans()

        self.assertEqual(len(spans), 1)
        self.assertEqual(spans[0].name, 'testing.nonfilteredurl')
