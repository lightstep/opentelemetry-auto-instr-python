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

from pylons.controllers import WSGIController

from ..lib.helpers import ExceptionWithCodeMethod, get_render_fn


class BaseController(WSGIController):

    def __call__(self, environ, start_response):
        """Invoke the Controller"""
        # WSGIController.__call__ dispatches to the Controller method
        # the request is routed to. This routing information is
        # available in environ['pylons.routes_dict']
        return WSGIController.__call__(self, environ, start_response)


class RootController(BaseController):
    """Controller used for most tests"""

    def index(self):
        return 'Hello World'

    def raise_exception(self):
        raise Exception('Ouch!')

    def raise_wrong_code(self):
        e = Exception('Ouch!')
        e.code = 'wrong formatted code'
        raise e

    def raise_code_method(self):
        raise ExceptionWithCodeMethod('Ouch!')

    def raise_custom_code(self):
        e = Exception('Ouch!')
        e.code = '512'
        raise e

    def render(self):
        render = get_render_fn()
        return render('/template.mako')

    def render_exception(self):
        render = get_render_fn()
        return render('/exception.mako')
