import os
from oteltrace.vendor import wrapt
import falcon

from oteltrace import tracer

from .middleware import TraceMiddleware
from ...utils.formats import asbool, get_env


def patch():
    """
    Patch falcon.API to include contrib.falcon.TraceMiddleware
    by default
    """
    if getattr(falcon, '_opentelemetry_patch', False):
        return

    setattr(falcon, '_opentelemetry_patch', True)
    wrapt.wrap_function_wrapper('falcon', 'API.__init__', traced_init)


def traced_init(wrapped, instance, args, kwargs):
    mw = kwargs.pop('middleware', [])
    service = os.environ.get('OPENTELEMETRY_SERVICE_NAME') or 'falcon'
    distributed_tracing = asbool(get_env('falcon', 'distributed_tracing', True))

    mw.insert(0, TraceMiddleware(tracer, service, distributed_tracing))
    kwargs['middleware'] = mw

    wrapped(*args, **kwargs)
