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

import pylons

from pylons import config

from oteltrace.vendor.wrapt import wrap_function_wrapper as _w

from .compat import legacy_pylons
from .constants import CONFIG_MIDDLEWARE


def trace_rendering():
    """Patch all Pylons renderers. It supports multiple versions
    of Pylons and multiple renderers.
    """
    # patch only once
    if getattr(pylons.templating, '__opentelemetry_patch', False):
        return
    setattr(pylons.templating, '__opentelemetry_patch', True)

    if legacy_pylons:
        # Pylons <= 0.9.7
        _w('pylons.templating', 'render', _traced_renderer)
    else:
        # Pylons > 0.9.7
        _w('pylons.templating', 'render_mako', _traced_renderer)
        _w('pylons.templating', 'render_mako_def', _traced_renderer)
        _w('pylons.templating', 'render_genshi', _traced_renderer)
        _w('pylons.templating', 'render_jinja2', _traced_renderer)


def _traced_renderer(wrapped, instance, args, kwargs):
    """Traced renderer"""
    tracer = config[CONFIG_MIDDLEWARE]._tracer
    with tracer.trace('pylons.render') as span:
        span.set_tag('template.name', args[0])
        return wrapped(*args, **kwargs)
