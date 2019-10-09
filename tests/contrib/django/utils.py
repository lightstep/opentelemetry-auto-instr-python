from functools import wraps

# 3rd party
from django.apps import apps
from django.test import TestCase

# project
from oteltrace.tracer import Tracer
from oteltrace.contrib.django.conf import settings
from oteltrace.contrib.django.db import patch_db, unpatch_db
from oteltrace.contrib.django.cache import unpatch_cache
from oteltrace.contrib.django.templates import unpatch_template
from oteltrace.contrib.django.middleware import remove_exception_middleware, remove_trace_middleware

# testing
from ...base import BaseTestCase
from ...test_tracer import DummyWriter


# testing tracer
tracer = Tracer()
tracer.writer = DummyWriter()


class DjangoTraceTestCase(BaseTestCase, TestCase):
    """
    Base class that provides an internal tracer according to given
    OpenTelemetry settings. This class ensures that the tracer spans are
    properly reset after each run. The tracer is available in
    the ``self.tracer`` attribute.
    """
    def setUp(self):
        # assign the default tracer
        self.tracer = settings.TRACER
        # empty the tracer spans from previous operations
        # such as database creation queries
        self.tracer.writer.spans = []
        self.tracer.writer.pop_traces()
        # gets unpatched for some tests
        patch_db(self.tracer)

    def tearDown(self):
        # empty the tracer spans from test operations
        self.tracer.writer.spans = []
        self.tracer.writer.pop_traces()


class override_oteltrace_settings(object):
    def __init__(self, *args, **kwargs):
        self.items = list(kwargs.items())

    def unpatch_all(self):
        unpatch_cache()
        unpatch_db()
        unpatch_template()
        remove_trace_middleware()
        remove_exception_middleware()

    def __enter__(self):
        self.enable()

    def __exit__(self, exc_type, exc_value, traceback):
        self.disable()

    def enable(self):
        self.backup = {}
        for name, value in self.items:
            self.backup[name] = getattr(settings, name)
            setattr(settings, name, value)
        self.unpatch_all()
        app = apps.get_app_config('opentelemetry_django')
        app.ready()

    def disable(self):
        for name, value in self.items:
            setattr(settings, name, self.backup[name])
        self.unpatch_all()
        remove_exception_middleware()
        app = apps.get_app_config('opentelemetry_django')
        app.ready()

    def __call__(self, func):
        @wraps(func)
        def inner(*args, **kwargs):
            with(self):
                return func(*args, **kwargs)
        return inner
