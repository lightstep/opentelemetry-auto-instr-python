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
The ``jinja2`` integration traces templates loading, compilation and rendering.
Auto instrumentation is available using the ``patch``. The following is an example::

    from oteltrace import patch
    from jinja2 import Environment, FileSystemLoader

    patch(jinja2=True)

    env = Environment(
        loader=FileSystemLoader("templates")
    )
    template = env.get_template('mytemplate.html')


The library can be configured globally and per instance, using the Configuration API::

    from oteltrace import config

    # Change service name globally
    config.jinja2['service_name'] = 'jinja-templates'

    # change the service name only for this environment
    cfg = config.get_from(env)
    cfg['service_name'] = 'jinja-templates'

By default, the service name is set to None, so it is inherited from the parent span.
If there is no parent span and the service name is not overriden the agent will drop the traces.
"""
from ...utils.importlib import require_modules


required_modules = ['jinja2']

with require_modules(required_modules) as missing_modules:
    if not missing_modules:
        from .patch import patch, unpatch

        __all__ = [
            'patch',
            'unpatch',
        ]
