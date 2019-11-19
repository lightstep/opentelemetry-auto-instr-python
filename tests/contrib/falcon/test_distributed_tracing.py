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

from falcon import testing
from tests.test_tracer import get_dummy_tracer

from .app import get_app


class DistributedTracingTestCase(testing.TestCase):
    """Executes tests using the manual instrumentation so a middleware
    is explicitly added.
    """

    def setUp(self):
        super(DistributedTracingTestCase, self).setUp()
        self._service = 'falcon'
        self.tracer = get_dummy_tracer()
        self.api = get_app(tracer=self.tracer)

    def test_distributred_tracing(self):
        headers = {
            'x-datadog-trace-id': '100',
            'x-datadog-parent-id': '42',
        }
        out = self.simulate_get('/200', headers=headers)
        assert out.status_code == 200
        assert out.content.decode('utf-8') == 'Success'

        traces = self.tracer.writer.pop_traces()

        assert len(traces) == 1
        assert len(traces[0]) == 1

        assert traces[0][0].parent_id == 42
        assert traces[0][0].trace_id == 100

    def test_distributred_tracing_disabled(self):
        self.tracer = get_dummy_tracer()
        self.api = get_app(tracer=self.tracer, distributed_tracing=False)
        headers = {
            'x-datadog-trace-id': '100',
            'x-datadog-parent-id': '42',
        }
        out = self.simulate_get('/200', headers=headers)
        assert out.status_code == 200
        assert out.content.decode('utf-8') == 'Success'

        traces = self.tracer.writer.pop_traces()

        assert len(traces) == 1
        assert len(traces[0]) == 1

        assert traces[0][0].parent_id != 42
        assert traces[0][0].trace_id != 100
