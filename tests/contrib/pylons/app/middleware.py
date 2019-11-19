# Copyright 2019, OpenTelemetry Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from webob import Request, Response


class ExceptionMiddleware(object):
    """A middleware which raises an exception."""
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        raise Exception('Middleware exception')


class ExceptionToSuccessMiddleware(object):
    """A middleware which catches any exceptions that occur in a later
    middleware and returns a successful request.
    """
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        req = Request(environ)
        try:
            response = req.get_response(self.app)
        except Exception:
            response = Response()
            response.status_int = 200
            response.body = 'An error has been handled appropriately'
        return response(environ, start_response)


class ExceptionToClientErrorMiddleware(object):
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        req = Request(environ)
        try:
            response = req.get_response(self.app)
        except Exception:
            response = Response()
            response.status_int = 404
            response.body = 'An error has occured with proper client error handling'
        return response(environ, start_response)
