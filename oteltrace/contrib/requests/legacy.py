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

# [Deprecation]: this module contains deprecated functions
# that will be removed in newer versions of the Tracer.
from oteltrace import config

from ...utils.deprecation import deprecation


def _distributed_tracing(self):
    """Deprecated: this method has been deprecated in favor of
    the configuration system. It will be removed in newer versions
    of the Tracer.
    """
    deprecation(
        name='client.distributed_tracing',
        message='Use the configuration object instead `config.get_from(client)[\'distributed_tracing\'`',
        version='1.0.0',
    )
    return config.get_from(self)['distributed_tracing']


def _distributed_tracing_setter(self, value):
    """Deprecated: this method has been deprecated in favor of
    the configuration system. It will be removed in newer versions
    of the Tracer.
    """
    deprecation(
        name='client.distributed_tracing',
        message='Use the configuration object instead `config.get_from(client)[\'distributed_tracing\'] = value`',
        version='1.0.0',
    )
    config.get_from(self)['distributed_tracing'] = value
