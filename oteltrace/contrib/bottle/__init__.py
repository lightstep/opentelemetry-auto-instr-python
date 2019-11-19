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
The bottle integration traces the Bottle web framework. Add the following
plugin to your app::

    import bottle
    from oteltrace import tracer
    from oteltrace.contrib.bottle import TracePlugin

    app = bottle.Bottle()
    plugin = TracePlugin(service="my-web-app")
    app.install(plugin)
"""

from ...utils.importlib import require_modules

required_modules = ['bottle']

with require_modules(required_modules) as missing_modules:
    if not missing_modules:
        from .trace import TracePlugin
        from .patch import patch

        __all__ = ['TracePlugin', 'patch']
