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

import unittest

import oteltrace.propagation.b3 as b3_format
from oteltrace.span import _new_id

FORMAT = b3_format.B3HTTPPropagator()


class TestB3Format(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.serialized_trace_id = b3_format.format_trace_id(
            _new_id()
        )
        cls.serialized_span_id = b3_format.format_span_id(
            _new_id()
        )

    def test_extract_multi_header(self):
        """Test the extraction of B3 headers."""
        carrier = {
            FORMAT.TRACE_ID_KEY: self.serialized_trace_id,
            FORMAT.SPAN_ID_KEY: self.serialized_span_id,
            FORMAT.SAMPLED_KEY: '1',
        }
        span_context = FORMAT.extract(carrier)
        new_carrier = {}
        FORMAT.inject(span_context, new_carrier)
        self.assertEqual(
            new_carrier[FORMAT.TRACE_ID_KEY], self.serialized_trace_id
        )
        self.assertEqual(
            new_carrier[FORMAT.SPAN_ID_KEY], self.serialized_span_id
        )
        self.assertEqual(new_carrier[FORMAT.SAMPLED_KEY], '1')

    def test_extract_single_header(self):
        """Test the extraction from a single b3 header."""
        carrier = {
            FORMAT.SINGLE_HEADER_KEY: '{}-{}'.format(
                self.serialized_trace_id, self.serialized_span_id
            )
        }
        span_context = FORMAT.extract(carrier)
        new_carrier = {}
        FORMAT.inject(span_context, new_carrier)
        self.assertEqual(
            new_carrier[FORMAT.TRACE_ID_KEY], self.serialized_trace_id
        )
        self.assertEqual(
            new_carrier[FORMAT.SPAN_ID_KEY], self.serialized_span_id
        )
        self.assertEqual(new_carrier[FORMAT.SAMPLED_KEY], '1')

    def test_extract_header_precedence(self):
        """A single b3 header should take precedence over multiple
        headers.
        """
        single_header_trace_id = self.serialized_trace_id[:-3] + '123'
        carrier = {
            FORMAT.SINGLE_HEADER_KEY: '{}-{}'.format(
                single_header_trace_id, self.serialized_span_id
            ),
            FORMAT.TRACE_ID_KEY: self.serialized_trace_id,
            FORMAT.SPAN_ID_KEY: self.serialized_span_id,
            FORMAT.SAMPLED_KEY: '1',
        }
        span_context = FORMAT.extract(carrier)
        new_carrier = {}
        FORMAT.inject(span_context, new_carrier)
        self.assertEqual(
            new_carrier[FORMAT.TRACE_ID_KEY], single_header_trace_id
        )

    def test_enabled_sampling(self):
        """Test b3 sample key variants that turn on sampling."""
        for variant in ['1', 'True', 'true', 'd']:
            carrier = {
                FORMAT.TRACE_ID_KEY: self.serialized_trace_id,
                FORMAT.SPAN_ID_KEY: self.serialized_span_id,
                FORMAT.SAMPLED_KEY: variant,
            }
            span_context = FORMAT.extract(carrier)
            new_carrier = {}
            FORMAT.inject(span_context, new_carrier)
            self.assertEqual(new_carrier[FORMAT.SAMPLED_KEY], '1')

    def test_disabled_sampling(self):
        """Test b3 sample key variants that turn off sampling."""
        for variant in ['0', 'False', 'false', None]:
            carrier = {
                FORMAT.TRACE_ID_KEY: self.serialized_trace_id,
                FORMAT.SPAN_ID_KEY: self.serialized_span_id,
                FORMAT.SAMPLED_KEY: variant,
            }
            span_context = FORMAT.extract(carrier)
            new_carrier = {}
            FORMAT.inject(span_context, new_carrier)
            self.assertEqual(new_carrier[FORMAT.SAMPLED_KEY], '0')

    def test_flags(self):
        """x-b3-flags set to '1' should result in propagation."""
        carrier = {
            FORMAT.TRACE_ID_KEY: self.serialized_trace_id,
            FORMAT.SPAN_ID_KEY: self.serialized_span_id,
            FORMAT.FLAGS_KEY: '1',
        }
        span_context = FORMAT.extract(carrier)
        new_carrier = {}
        FORMAT.inject(span_context, new_carrier)
        self.assertEqual(new_carrier[FORMAT.SAMPLED_KEY], '1')

    def test_flags_and_sampling(self):
        """Propagate if b3 flags and sampling are set."""
        carrier = {
            FORMAT.TRACE_ID_KEY: self.serialized_trace_id,
            FORMAT.SPAN_ID_KEY: self.serialized_span_id,
            FORMAT.FLAGS_KEY: '1',
        }
        span_context = FORMAT.extract(carrier)
        new_carrier = {}
        FORMAT.inject(span_context, new_carrier)
        self.assertEqual(new_carrier[FORMAT.SAMPLED_KEY], '1')

    def test_64bit_trace_id(self):
        """64 bit trace ids should be padded to 128 bit trace ids."""
        trace_id_64_bit = self.serialized_trace_id[:16]
        carrier = {
            FORMAT.TRACE_ID_KEY: trace_id_64_bit,
            FORMAT.SPAN_ID_KEY: self.serialized_span_id,
            FORMAT.FLAGS_KEY: '1',
        }
        span_context = FORMAT.extract(carrier)
        new_carrier = {}
        FORMAT.inject(span_context, new_carrier)
        self.assertEqual(
            new_carrier[FORMAT.TRACE_ID_KEY], '0' * 16 + trace_id_64_bit
        )

    def test_invalid_single_header(self):
        """If an invalid single header is passed, return an
        invalid SpanContext.
        """
        carrier = {FORMAT.SINGLE_HEADER_KEY: '0-1-2-3-4-5-6-7'}
        span_context = FORMAT.extract(carrier)
        self.assertIsNone(span_context.trace_id)
        self.assertIsNone(span_context.span_id)

    def test_missing_trace_id(self):
        """If a trace id is missing, populate an invalid trace id."""
        carrier = {
            FORMAT.SPAN_ID_KEY: self.serialized_span_id,
            FORMAT.FLAGS_KEY: '1',
        }
        span_context = FORMAT.extract(carrier)
        self.assertEqual(span_context.trace_id, 0)

    def test_missing_span_id(self):
        """If a trace id is missing, populate an invalid trace id."""
        carrier = {
            FORMAT.TRACE_ID_KEY: self.serialized_trace_id,
            FORMAT.FLAGS_KEY: '1',
        }
        span_context = FORMAT.extract(carrier)
        self.assertEqual(span_context.span_id, 0)
