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

import falcon


class Resource200(object):
    """Throw a handled exception here to ensure our use of
    set_traceback() doesn't affect 200s
    """
    def on_get(self, req, resp, **kwargs):
        try:
            1 / 0
        except Exception:
            pass

        resp.status = falcon.HTTP_200
        resp.body = 'Success'
        resp.append_header('my-response-header', 'my_response_value')


class Resource201(object):
    def on_post(self, req, resp, **kwargs):
        resp.status = falcon.HTTP_201
        resp.body = 'Success'


class Resource500(object):
    def on_get(self, req, resp, **kwargs):
        resp.status = falcon.HTTP_500
        resp.body = 'Failure'


class ResourceException(object):
    def on_get(self, req, resp, **kwargs):
        raise Exception('Ouch!')


class ResourceNotFound(object):
    def on_get(self, req, resp, **kwargs):
        # simulate that the endpoint is hit but raise a 404 because
        # the object isn't found in the database
        raise falcon.HTTPNotFound()
