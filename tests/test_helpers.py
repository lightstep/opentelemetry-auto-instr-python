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

from oteltrace import helpers

from .base import BaseTracerTestCase
from .util import override_global_tracer


class HelpersTestCase(BaseTracerTestCase):
    """Test suite for ``oteltrace`` helpers"""
    def test_correlation_identifiers(self):
        # ensures the right correlation identifiers are
        # returned when a Trace is active
        with override_global_tracer(self.tracer):
            span = self.tracer.trace('MockSpan')
            active_trace_id, active_span_id = span.trace_id, span.span_id
            trace_id, span_id = helpers.get_correlation_ids()

        self.assertEqual(trace_id, active_trace_id)
        self.assertEqual(span_id, active_span_id)

    def test_correlation_identifiers_without_trace(self):
        # ensures `None` is returned if no Traces are active
        with override_global_tracer(self.tracer):
            trace_id, span_id = helpers.get_correlation_ids()

        self.assertIsNone(trace_id)
        self.assertIsNone(span_id)

    def test_correlation_identifiers_with_disabled_trace(self):
        # ensures `None` is returned if tracer is disabled
        with override_global_tracer(self.tracer):
            self.tracer.enabled = False
            self.tracer.trace('MockSpan')
            trace_id, span_id = helpers.get_correlation_ids()

        self.assertIsNone(trace_id)
        self.assertIsNone(span_id)

    def test_correlation_identifiers_missing_context(self):
        # ensures we return `None` if there is no current context
        self.tracer.get_call_context = mock.MagicMock(return_value=None)

        with override_global_tracer(self.tracer):
            trace_id, span_id = helpers.get_correlation_ids()

        self.assertIsNone(trace_id)
        self.assertIsNone(span_id)
