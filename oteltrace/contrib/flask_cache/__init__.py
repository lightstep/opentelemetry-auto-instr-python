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

"""
The flask cache tracer will track any access to a cache backend.
You can use this tracer together with the Flask tracer middleware.

To install the tracer, ``from oteltrace import tracer`` needs to be added::

    from oteltrace import tracer
    from oteltrace.contrib.flask_cache import get_traced_cache

and the tracer needs to be initialized::

    Cache = get_traced_cache(tracer, service='my-flask-cache-app')

Here is the end result, in a sample app::

    from flask import Flask

    from oteltrace import tracer
    from oteltrace.contrib.flask_cache import get_traced_cache

    app = Flask(__name__)

    # get the traced Cache class
    Cache = get_traced_cache(tracer, service='my-flask-cache-app')

    # use the Cache as usual with your preferred CACHE_TYPE
    cache = Cache(app, config={'CACHE_TYPE': 'simple'})

    def counter():
        # this access is traced
        conn_counter = cache.get("conn_counter")

"""

from ...utils.importlib import require_modules


required_modules = ['flask_cache']

with require_modules(required_modules) as missing_modules:
    if not missing_modules:
        from .tracers import get_traced_cache

        __all__ = ['get_traced_cache']
