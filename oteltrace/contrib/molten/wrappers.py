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
import molten

from ... import Pin
from ...utils.importlib import func_name

MOLTEN_ROUTE = 'molten.route'


def trace_wrapped(resource, wrapped, *args, **kwargs):
    pin = Pin.get_from(molten)
    if not pin or not pin.enabled():
        return wrapped(*args, **kwargs)

    with pin.tracer.trace(func_name(wrapped), service=pin.service, resource=resource):
        return wrapped(*args, **kwargs)


def trace_func(resource):
    """Trace calls to function using provided resource name
    """
    @wrapt.function_wrapper
    def _trace_func(wrapped, instance, args, kwargs):
        pin = Pin.get_from(molten)

        if not pin or not pin.enabled():
            return wrapped(*args, **kwargs)

        with pin.tracer.trace(func_name(wrapped), service=pin.service, resource=resource):
            return wrapped(*args, **kwargs)

    return _trace_func


class WrapperComponent(wrapt.ObjectProxy):
    """ Tracing of components """
    def can_handle_parameter(self, *args, **kwargs):
        func = self.__wrapped__.can_handle_parameter
        cname = func_name(self.__wrapped__)
        resource = '{}.{}'.format(cname, func.__name__)
        return trace_wrapped(resource, func, *args, **kwargs)

    # TODO[tahir]: the signature of a wrapped resolve method causes DIError to
    # be thrown since paramter types cannot be determined


class WrapperRenderer(wrapt.ObjectProxy):
    """ Tracing of renderers """
    def render(self, *args, **kwargs):
        func = self.__wrapped__.render
        cname = func_name(self.__wrapped__)
        resource = '{}.{}'.format(cname, func.__name__)
        return trace_wrapped(resource, func, *args, **kwargs)


class WrapperMiddleware(wrapt.ObjectProxy):
    """ Tracing of callable functional-middleware """
    def __call__(self, *args, **kwargs):
        func = self.__wrapped__.__call__
        resource = func_name(self.__wrapped__)
        return trace_wrapped(resource, func, *args, **kwargs)


class WrapperRouter(wrapt.ObjectProxy):
    """ Tracing of router on the way back from a matched route """
    def match(self, *args, **kwargs):
        # catch matched route and wrap tracer around its handler and set root span resource
        func = self.__wrapped__.match
        route_and_params = func(*args, **kwargs)

        pin = Pin.get_from(molten)
        if not pin or not pin.enabled():
            return route_and_params

        if route_and_params is not None:
            route, params = route_and_params

            route.handler = trace_func(func_name(route.handler))(route.handler)

            # update root span resource while we know the matched route
            resource = '{} {}'.format(
                route.method,
                route.template,
            )
            root_span = pin.tracer.current_root_span()
            root_span.resource = resource

            # if no root route set make sure we record it based on this resolved
            # route
            if root_span and not root_span.get_tag(MOLTEN_ROUTE):
                root_span.set_tag(MOLTEN_ROUTE, route.name)

            return route, params

        return route_and_params
