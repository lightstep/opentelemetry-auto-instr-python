from ddtrace.filters import FilterRequestsOnUrl

from .utils import TornadoTestCase


class TestTornadoSettings(TornadoTestCase):
    """
    Ensure that Tornado web Application configures properly
    the given tracer.
    """
    def get_settings(self):
        # update tracer settings
        return {
            'datadog_trace': {
                'default_service': 'custom-tornado',
                'tags': {'env': 'production', 'debug': 'false'},
                'enabled': False,
                'settings': {
                    'FILTERS':  [
                        FilterRequestsOnUrl(r'http://test\.example\.com'),
                    ],
                },
            },
        }

    def test_tracer_is_properly_configured(self):
        # the tracer must be properly configured
        assert self.tracer.tags == {'env': 'production', 'debug': 'false'}
        assert self.tracer.enabled is False
        # settings are properly passed
        assert self.tracer.writer._filters is not None
        assert len(self.tracer.writer._filters) == 1
        assert isinstance(self.tracer.writer._filters[0], FilterRequestsOnUrl)
