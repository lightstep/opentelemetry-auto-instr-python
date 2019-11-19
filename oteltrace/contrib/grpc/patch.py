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

import grpc
import os

from oteltrace.vendor.wrapt import wrap_function_wrapper as _w
from oteltrace import config, Pin

from ...utils.wrappers import unwrap as _u

from . import constants
from .client_interceptor import create_client_interceptor, intercept_channel
from .server_interceptor import create_server_interceptor


config._add('grpc_server', dict(
    service_name=os.environ.get('OPENTELEMETRY_SERVICE_NAME', constants.GRPC_SERVICE_SERVER),
    distributed_tracing_enabled=True,
))

# TODO[tbutt]: keeping name for client config unchanged to maintain backwards
# compatibility but should change in future
config._add('grpc', dict(
    service_name='{}-{}'.format(
        os.environ.get('OPENTELEMETRY_SERVICE_NAME'), constants.GRPC_SERVICE_CLIENT
    ) if os.environ.get('OPENTELEMETRY_SERVICE_NAME') else constants.GRPC_SERVICE_CLIENT,
    distributed_tracing_enabled=True,
))


def patch():
    _patch_client()
    _patch_server()


def unpatch():
    _unpatch_client()
    _unpatch_server()


def _patch_client():
    if getattr(constants.GRPC_PIN_MODULE_CLIENT, '__opentelemetry_patch', False):
        return
    setattr(constants.GRPC_PIN_MODULE_CLIENT, '__opentelemetry_patch', True)

    Pin(service=config.grpc.service_name).onto(constants.GRPC_PIN_MODULE_CLIENT)

    _w('grpc', 'insecure_channel', _client_channel_interceptor)
    _w('grpc', 'secure_channel', _client_channel_interceptor)
    _w('grpc', 'intercept_channel', intercept_channel)


def _unpatch_client():
    if not getattr(constants.GRPC_PIN_MODULE_CLIENT, '__opentelemetry_patch', False):
        return
    setattr(constants.GRPC_PIN_MODULE_CLIENT, '__opentelemetry_patch', False)

    pin = Pin.get_from(constants.GRPC_PIN_MODULE_CLIENT)
    if pin:
        pin.remove_from(constants.GRPC_PIN_MODULE_CLIENT)

    _u(grpc, 'secure_channel')
    _u(grpc, 'insecure_channel')


def _patch_server():
    if getattr(constants.GRPC_PIN_MODULE_SERVER, '__opentelemetry_patch', False):
        return
    setattr(constants.GRPC_PIN_MODULE_SERVER, '__opentelemetry_patch', True)

    Pin(service=config.grpc_server.service_name).onto(constants.GRPC_PIN_MODULE_SERVER)

    _w('grpc', 'server', _server_constructor_interceptor)


def _unpatch_server():
    if not getattr(constants.GRPC_PIN_MODULE_SERVER, '__opentelemetry_patch', False):
        return
    setattr(constants.GRPC_PIN_MODULE_SERVER, '__opentelemetry_patch', False)

    pin = Pin.get_from(constants.GRPC_PIN_MODULE_SERVER)
    if pin:
        pin.remove_from(constants.GRPC_PIN_MODULE_SERVER)

    _u(grpc, 'server')


def _client_channel_interceptor(wrapped, instance, args, kwargs):
    channel = wrapped(*args, **kwargs)

    pin = Pin.get_from(constants.GRPC_PIN_MODULE_CLIENT)
    if not pin or not pin.enabled():
        return channel

    (host, port) = _parse_target_from_arguments(args, kwargs)

    interceptor_function = create_client_interceptor(pin, host, port)
    return grpc.intercept_channel(channel, interceptor_function)


def _server_constructor_interceptor(wrapped, instance, args, kwargs):
    # DEV: we clone the pin on the grpc module and configure it for the server
    # interceptor

    pin = Pin.get_from(constants.GRPC_PIN_MODULE_SERVER)
    if not pin or not pin.enabled():
        return wrapped(*args, **kwargs)

    interceptor = create_server_interceptor(pin)

    # DEV: Inject our tracing interceptor first in the list of interceptors
    if 'interceptors' in kwargs:
        kwargs['interceptors'] = (interceptor,) + tuple(kwargs['interceptors'])
    else:
        kwargs['interceptors'] = (interceptor,)

    return wrapped(*args, **kwargs)


def _parse_target_from_arguments(args, kwargs):
    if 'target' in kwargs:
        target = kwargs['target']
    else:
        target = args[0]

    split = target.rsplit(':', 2)

    return (split[0], split[1] if len(split) > 1 else None)
