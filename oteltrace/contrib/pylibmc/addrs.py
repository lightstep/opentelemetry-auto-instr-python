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

translate_server_specs = None

try:
    # NOTE: we rely on an undocumented method to parse addresses,
    # so be a bit defensive and don't assume it exists.
    from pylibmc.client import translate_server_specs
except ImportError:
    pass


def parse_addresses(addrs):
    if not translate_server_specs:
        return []
    return translate_server_specs(addrs)
