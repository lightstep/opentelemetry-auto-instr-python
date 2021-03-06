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

import pytest
import tornado

from oteltrace.context import Context
from oteltrace.contrib.tornado import TracerStackContext

from .utils import TornadoTestCase
from .web.compat import sleep


class TestStackContext(TornadoTestCase):
    @pytest.mark.skipif(tornado.version_info >= (5, 0),
                        reason='tornado.stack_context deprecated in Tornado 5.0 and removed in Tornado 6.0')
    def test_without_stack_context(self):
        # without a TracerStackContext, propagation is not available
        ctx = self.tracer.context_provider.active()
        assert ctx is None

    def test_stack_context(self):
        # a TracerStackContext should automatically propagate a tracing context
        with TracerStackContext():
            ctx = self.tracer.context_provider.active()

        assert ctx is not None

    def test_propagation_with_new_context(self):
        # inside a TracerStackContext it should be possible to set
        # a new Context for distributed tracing
        with TracerStackContext():
            ctx = Context(trace_id=100, span_id=101)
            self.tracer.context_provider.activate(ctx)
            with self.tracer.trace('tornado'):
                sleep(0.01)

        traces = self.tracer.writer.pop_traces()
        assert len(traces) == 1
        assert len(traces[0]) == 1
        assert traces[0][0].trace_id == 100
        assert traces[0][0].parent_id == 101

    @pytest.mark.skipif(tornado.version_info >= (5, 0),
                        reason='tornado.stack_context deprecated in Tornado 5.0 and removed in Tornado 6.0')
    def test_propagation_without_stack_context(self):
        # a Context is discarded if not set inside a TracerStackContext
        ctx = Context(trace_id=100, span_id=101)
        self.tracer.context_provider.activate(ctx)
        with self.tracer.trace('tornado'):
            sleep(0.01)

        traces = self.tracer.writer.pop_traces()
        assert len(traces) == 1
        assert len(traces[0]) == 1
        assert traces[0][0].trace_id != 100
        assert traces[0][0].parent_id != 101
