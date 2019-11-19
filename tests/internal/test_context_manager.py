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

import threading

from oteltrace.context import Context
from oteltrace.internal.context_manager import DefaultContextManager
from oteltrace.span import Span

from ..base import BaseTestCase


class TestDefaultContextManager(BaseTestCase):
    """
    Ensures that a ``ContextManager`` makes the Context
    local to each thread or task.
    """
    def test_get_or_create(self):
        # asking the Context multiple times should return
        # always the same instance
        ctxm = DefaultContextManager()
        assert ctxm.get() == ctxm.get()

    def test_set_context(self):
        # the Context can be set in the current Thread
        ctx = Context()
        ctxm = DefaultContextManager()
        assert ctxm.get() is not ctx

        ctxm.set(ctx)
        assert ctxm.get() is ctx

    def test_multiple_threads_multiple_context(self):
        # each thread should have it's own Context
        ctxm = DefaultContextManager()

        def _fill_ctx():
            ctx = ctxm.get()
            span = Span(tracer=None, name='fake_span')
            ctx.add_span(span)
            assert 1 == len(ctx._trace)

        threads = [threading.Thread(target=_fill_ctx) for _ in range(100)]

        for t in threads:
            t.daemon = True
            t.start()

        for t in threads:
            t.join()

        # the main instance should have an empty Context
        # because it has not been used in this thread
        ctx = ctxm.get()
        assert 0 == len(ctx._trace)

    def test_reset_context_manager(self):
        ctxm = DefaultContextManager()
        ctx = ctxm.get()

        # new context manager should not share same context
        ctxm = DefaultContextManager()
        assert ctxm.get() is not ctx
