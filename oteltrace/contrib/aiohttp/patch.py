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

from oteltrace.vendor import wrapt

from ...pin import Pin
from ...utils.wrappers import unwrap


try:
    # instrument external packages only if they're available
    import aiohttp_jinja2
    from .template import _trace_render_template

    template_module = True
except ImportError:
    template_module = False


def patch():
    """
    Patch aiohttp third party modules:
        * aiohttp_jinja2
    """
    if template_module:
        if getattr(aiohttp_jinja2, '__opentelemetry_patch', False):
            return
        setattr(aiohttp_jinja2, '__opentelemetry_patch', True)

        _w = wrapt.wrap_function_wrapper
        _w('aiohttp_jinja2', 'render_template', _trace_render_template)
        Pin(app='aiohttp', service=None, app_type='web').onto(aiohttp_jinja2)


def unpatch():
    """
    Remove tracing from patched modules.
    """
    if template_module:
        if getattr(aiohttp_jinja2, '__opentelemetry_patch', False):
            setattr(aiohttp_jinja2, '__opentelemetry_patch', False)
            unwrap(aiohttp_jinja2, 'render_template')
