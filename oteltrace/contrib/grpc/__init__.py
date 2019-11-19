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
The gRPC integration traces the client and server using interceptor pattern.

gRPC will be automatically instrumented with ``patch_all``, or when using
the ``oteltrace-run`` command.
gRPC is instrumented on import. To instrument gRPC manually use the
``patch`` function.::

    import grpc
    from oteltrace import patch
    patch(grpc=True)

    # use grpc like usual

To configure the gRPC integration on an per-channel basis use the
``Pin`` API::

    import grpc
    from oteltrace import Pin, patch, Tracer

    patch(grpc=True)
    custom_tracer = Tracer()

    # override the pin on the client
    Pin.override(grpc.Channel, service='mygrpc', tracer=custom_tracer)
    with grpc.insecure_channel('localhost:50051') as channel:
        # create stubs and send requests
        pass

To configure the gRPC integration on the server use the ``Pin`` API::

    import grpc
    from grpc.framework.foundation import logging_pool

    from oteltrace import Pin, patch, Tracer

    patch(grpc=True)
    custom_tracer = Tracer()

    # override the pin on the server
    Pin.override(grpc.Server, service='mygrpc', tracer=custom_tracer)
    server = grpc.server(logging_pool.pool(2))
    server.add_insecure_port('localhost:50051')
    add_MyServicer_to_server(MyServicer(), server)
    server.start()
"""


from ...utils.importlib import require_modules

required_modules = ['grpc']

with require_modules(required_modules) as missing_modules:
    if not missing_modules:
        from .patch import patch, unpatch

        __all__ = ['patch', 'unpatch']
