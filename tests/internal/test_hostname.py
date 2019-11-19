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

import mock

from oteltrace.internal.hostname import get_hostname


@mock.patch('socket.gethostname')
def test_get_hostname(socket_gethostname):
    # Test that `get_hostname()` just returns `socket.gethostname`
    socket_gethostname.return_value = 'test-hostname'
    assert get_hostname() == 'test-hostname'

    # Change the value returned by `socket.gethostname` to test the cache
    socket_gethostname.return_value = 'new-hostname'
    assert get_hostname() == 'test-hostname'
