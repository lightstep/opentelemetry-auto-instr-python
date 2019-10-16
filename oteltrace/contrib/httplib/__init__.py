"""
Patch the built-in ``httplib``/``http.client`` libraries to trace all HTTP calls.


Usage::

    # Patch all supported modules/functions
    from oteltrace import patch
    patch(httplib=True)

    # Python 2
    import httplib
    import urllib

    resp = urllib.urlopen('http://opentelemetry.io/')

    # Python 3
    import http.client
    import urllib.request

    resp = urllib.request.urlopen('http://opentelemetry.io/')

``httplib`` spans do not include a default service name. Before HTTP calls are
made, ensure a parent span has been started with a service name to be used for
spans generated from those calls::

    with tracer.trace('main', service='my-httplib-operation'):
        resp = urllib.request.urlopen('http://opentelemetry.io/')

:ref:`Headers tracing <http-headers-tracing>` is supported for this integration.
"""
from .patch import patch, unpatch
__all__ = ['patch', 'unpatch']
