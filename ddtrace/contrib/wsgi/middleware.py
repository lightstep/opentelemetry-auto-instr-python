import wsgiref.util

from ...ext import http
from ...pin import Pin
from .utils import wrap_start_response


class TracedWSGIMiddleware(object):
    __slots__ = ('app', 'name', '_datadog_pin')

    def __init__(self, app, name='wsgi.request'):
        self.app = app
        self.name = name

    def get_pin(self):
        return Pin._find(self, self.app)

    def __call__(self, environ, start_response):
        pin = self.get_pin()
        if not pin or not pin.enabled():
            return self.app(environ, start_response)

        # Determine the resource name
        # <METHOD> <PATH_INFO>
        # Example:
        #   GET /
        #   GET /user/1234/info
        #   POST /user/add
        # DEV: These resources have a high cardinality since `/user/1234` is seen as a different resource as `/user/abcd`
        path = environ.get('PATH_INFO')
        method = environ.get('REQUEST_METHOD')
        resource = u'{} {}'.format(method, path)

        # Start the trace
        with pin.tracer.trace(self.name, service=pin.service, resource=resource)as span:
            # Set tag for full request uri, e.g. `http://127.0.0.1:8000/users/abcd?force=true`
            span.set_tag(http.URL, wsgiref.util.request_uri(environ))
            # Set tag for request method
            span.set_tag(http.METHOD, method)

            # Call the original WSGI function with a wrapped `start_response`
            # DEV: `start_response` we set error and response tags
            return self.app(environ, wrap_start_response(start_response, span))
