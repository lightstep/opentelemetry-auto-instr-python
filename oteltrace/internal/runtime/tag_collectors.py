from .collector import ValueCollector
from .constants import (
    SERVICE,
    LANG_INTERPRETER,
    LANG_VERSION,
    LANG,
    TRACER_VERSION,
)
from ...constants import ENV_KEY


class RuntimeTagCollector(ValueCollector):
    periodic = False
    value = []


class TracerTagCollector(RuntimeTagCollector):
    """ Tag collector for the oteltrace Tracer
    """
    required_modules = ['oteltrace']

    def collect_fn(self, keys):
        oteltrace = self.modules.get('oteltrace')
        tags = [(SERVICE, service) for service in oteltrace.tracer._services]
        if ENV_KEY in oteltrace.tracer.tags:
            tags.append((ENV_KEY, oteltrace.tracer.tags[ENV_KEY]))
        return tags


class PlatformTagCollector(RuntimeTagCollector):
    """ Tag collector for the Python interpreter implementation.

    Tags collected:
    - lang_interpreter:
      - For CPython this is 'CPython'.
      - For Pypy this is 'PyPy'.
      - For Jython this is 'Jython'.
    - lang_version:
      - eg. '2.7.10'
    - lang:
      - e.g. 'Python'
    - tracer_version:
      - e.g. '0.29.0'
    """
    required_modules = ('platform', 'oteltrace')

    def collect_fn(self, keys):
        platform = self.modules.get('platform')
        oteltrace = self.modules.get('oteltrace')
        tags = [
            (LANG, 'python'),
            (LANG_INTERPRETER, platform.python_implementation()),
            (LANG_VERSION, platform.python_version()),
            (TRACER_VERSION, oteltrace.__version__),
        ]
        return tags
