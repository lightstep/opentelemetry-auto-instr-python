from oteltrace.propagation.utils import get_wsgi_header


class TestPropagationUtils(object):
    def test_get_wsgi_header(self):
        assert get_wsgi_header('x-opentelemetry-trace-id') == 'HTTP_X_OPENTELEMETRY_TRACE_ID'
