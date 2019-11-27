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

import mako
from mako.template import Template

from ...ext import http
from ...pin import Pin
from ...utils.importlib import func_name
from ...utils.wrappers import unwrap as _u
from ...vendor.wrapt import wrap_function_wrapper as _w
from .constants import DEFAULT_TEMPLATE_NAME


def patch():
    if getattr(mako, '__opentelemetry_patch', False):
        # already patched
        return
    setattr(mako, '__opentelemetry_patch', True)

    Pin(service='mako', app='mako', app_type=http.TEMPLATE).onto(Template)

    _w(mako, 'template.Template.render', _wrap_render)
    _w(mako, 'template.Template.render_unicode', _wrap_render)
    _w(mako, 'template.Template.render_context', _wrap_render)


def unpatch():
    if not getattr(mako, '__opentelemetry_patch', False):
        return
    setattr(mako, '__opentelemetry_patch', False)

    _u(mako.template.Template, 'render')
    _u(mako.template.Template, 'render_unicode')
    _u(mako.template.Template, 'render_context')


def _wrap_render(wrapped, instance, args, kwargs):
    pin = Pin.get_from(instance)
    if not pin or not pin.enabled():
        return wrapped(*args, **kwargs)

    template_name = instance.filename or DEFAULT_TEMPLATE_NAME
    with pin.tracer.trace(func_name(wrapped), pin.service, span_type=http.TEMPLATE) as span:
        try:
            template = wrapped(*args, **kwargs)
            return template
        finally:
            span.resource = template_name
            span.set_tag('mako.template_name', template_name)
