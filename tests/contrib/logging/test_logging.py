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

import logging

from oteltrace.helpers import get_correlation_ids
from oteltrace.compat import StringIO
from oteltrace.contrib.logging import patch, unpatch
from oteltrace.vendor import wrapt

from ...base import BaseTracerTestCase


logger = logging.getLogger()
logger.level = logging.INFO


def capture_function_log(func, fmt):
    # add stream handler to capture output
    out = StringIO()
    sh = logging.StreamHandler(out)

    try:
        formatter = logging.Formatter(fmt)
        sh.setFormatter(formatter)
        logger.addHandler(sh)
        result = func()
    finally:
        logger.removeHandler(sh)

    return out.getvalue().strip(), result


class LoggingTestCase(BaseTracerTestCase):
    def setUp(self):
        patch()
        super(LoggingTestCase, self).setUp()

    def tearDown(self):
        unpatch()
        super(LoggingTestCase, self).tearDown()

    def test_patch(self):
        """
        Confirm patching was successful
        """
        patch()
        log = logging.getLogger()
        self.assertTrue(isinstance(log.makeRecord, wrapt.BoundFunctionWrapper))

    def test_log_trace(self):
        """
        Check logging patched and formatter including trace info
        """
        @self.tracer.wrap()
        def func():
            logger.info('Hello!')
            return get_correlation_ids(tracer=self.tracer)

        with self.override_config('logging', dict(tracer=self.tracer)):
            # with format string for trace info
            output, result = capture_function_log(
                func,
                fmt='%(message)s - otel.trace_id=%(otel.trace_id)s otel.span_id=%(otel.span_id)s',
            )
            self.assertEqual(
                output,
                'Hello! - otel.trace_id={} otel.span_id={}'.format(*result),
            )

            # without format string
            output, _ = capture_function_log(
                func,
                fmt='%(message)s',
            )
            self.assertEqual(
                output,
                'Hello!',
            )

    def test_log_no_trace(self):
        """
        Check traced funclogging patched and formatter not including trace info
        """
        def func():
            logger.info('Hello!')
            return get_correlation_ids()

        with self.override_config('logging', dict(tracer=self.tracer)):
            # with format string for trace info
            output, _ = capture_function_log(
                func,
                fmt='%(message)s - otel.trace_id=%(otel.trace_id)s otel.span_id=%(otel.span_id)s',
            )
            self.assertEqual(
                output,
                'Hello! - otel.trace_id=0 otel.span_id=0',
            )
