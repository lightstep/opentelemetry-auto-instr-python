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

from oteltrace.contrib.falcon import TraceMiddleware

from . import resources


def get_app(tracer=None, distributed_tracing=True):
    # initialize a traced Falcon application
    middleware = [TraceMiddleware(
        tracer, distributed_tracing=distributed_tracing)] if tracer else []
    app = falcon.API(middleware=middleware)

    # add resource routing
    app.add_route('/200', resources.Resource200())
    app.add_route('/201', resources.Resource201())
    app.add_route('/500', resources.Resource500())
    app.add_route('/exception', resources.ResourceException())
    app.add_route('/not_found', resources.ResourceNotFound())
    return app
