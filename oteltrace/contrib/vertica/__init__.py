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
The Vertica integration will trace queries made using the vertica-python
library.

Vertica will be automatically instrumented with ``patch_all``, or when using
the ``oteltrace-run`` command.

Vertica is instrumented on import. To instrument Vertica manually use the
``patch`` function. Note the ordering of the following statements::

    from oteltrace import patch
    patch(vertica=True)

    import vertica_python

    # use vertica_python like usual


To configure the Vertica integration globally you can use the ``Config`` API::

    from oteltrace import config, patch
    patch(vertica=True)

    config.vertica['service_name'] = 'my-vertica-database'


To configure the Vertica integration on an instance-per-instance basis use the
``Pin`` API::

    from oteltrace import Pin, patch, Tracer
    patch(vertica=True)

    import vertica_python

    custom_tracer = Tracer()
    conn = vertica_python.connect(**YOUR_VERTICA_CONFIG)

    # override the service and tracer to be used
    Pin.override(conn, service='myverticaservice', tracer=custom_tracer)
"""

from ...utils.importlib import require_modules


required_modules = ['vertica_python']

with require_modules(required_modules) as missing_modules:
    if not missing_modules:
        from .patch import patch, unpatch

        __all__ = [patch, unpatch]
