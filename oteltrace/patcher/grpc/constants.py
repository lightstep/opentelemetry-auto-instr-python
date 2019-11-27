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


GRPC_PIN_MODULE_SERVER = grpc.Server
GRPC_PIN_MODULE_CLIENT = grpc.Channel
GRPC_METHOD_PATH_KEY = 'grpc.method.path'
GRPC_METHOD_PACKAGE_KEY = 'grpc.method.package'
GRPC_METHOD_SERVICE_KEY = 'grpc.method.service'
GRPC_METHOD_NAME_KEY = 'grpc.method.name'
GRPC_METHOD_KIND_KEY = 'grpc.method.kind'
GRPC_STATUS_CODE_KEY = 'grpc.status.code'
GRPC_REQUEST_METADATA_PREFIX_KEY = 'grpc.request.metadata.'
GRPC_RESPONSE_METADATA_PREFIX_KEY = 'grpc.response.metadata.'
GRPC_HOST_KEY = 'grpc.host'
GRPC_PORT_KEY = 'grpc.port'
GRPC_SPAN_KIND_KEY = 'span.kind'
GRPC_SPAN_KIND_VALUE_CLIENT = 'client'
GRPC_SPAN_KIND_VALUE_SERVER = 'server'
GRPC_METHOD_KIND_UNARY = 'unary'
GRPC_METHOD_KIND_CLIENT_STREAMING = 'client_streaming'
GRPC_METHOD_KIND_SERVER_STREAMING = 'server_streaming'
GRPC_METHOD_KIND_BIDI_STREAMING = 'bidi_streaming'
GRPC_SERVICE_SERVER = 'grpc-server'
GRPC_SERVICE_CLIENT = 'grpc-client'
