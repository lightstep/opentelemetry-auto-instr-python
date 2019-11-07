from unittest import TestCase, mock

from oteltrace.propagation import http as http_propagator_module
from oteltrace.propagation.http import DatadogHTTPPropagator

from oteltrace import tracer


class TestHTTPPropagator(TestCase):
    def test_default(self):
        prop = http_propagator_module.HTTPPropagator()
        self.assertIsInstance(prop, DatadogHTTPPropagator)

    def test_set_http_propagator_factory(self):
        mock_propagator = mock.Mock()

        def get_propagator():
            return mock_propagator

        http_propagator_module.set_http_propagator_factory(get_propagator)

        self.assertIs(http_propagator_module.HTTPPropagator(), mock_propagator)

    def test_tracer_configure_http_propagator(self):
        mock_propagator = mock.Mock()

        def get_propagator():
            return mock_propagator

        tracer.configure(http_propagator=get_propagator)

        self.assertIs(http_propagator_module.HTTPPropagator(), mock_propagator)
