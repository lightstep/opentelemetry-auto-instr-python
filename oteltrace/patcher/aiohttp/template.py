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

import aiohttp_jinja2

from oteltrace import Pin

from ...ext import http


def _trace_render_template(func, module, args, kwargs):
    """
    Trace the template rendering
    """
    # get the module pin
    pin = Pin.get_from(aiohttp_jinja2)
    if not pin or not pin.enabled():
        return func(*args, **kwargs)

    # original signature:
    # render_template(template_name, request, context, *, app_key=APP_KEY, encoding='utf-8')
    template_name = args[0]
    request = args[1]
    env = aiohttp_jinja2.get_env(request.app)

    # the prefix is available only on PackageLoader
    template_prefix = getattr(env.loader, 'package_path', '')
    template_meta = '{}/{}'.format(template_prefix, template_name)

    with pin.tracer.trace('aiohttp.template') as span:
        span.span_type = http.TEMPLATE
        span.set_meta('aiohttp.template', template_meta)
        return func(*args, **kwargs)
