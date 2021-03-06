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

from unittest import TestCase

from oteltrace.filters import FilterRequestsOnUrl
from oteltrace.span import Span
from oteltrace.ext.http import URL


class FilterRequestOnUrlTests(TestCase):
    def test_is_match(self):
        span = Span(name='Name', tracer=None)
        span.set_tag(URL, r'http://example.com')
        filtr = FilterRequestsOnUrl('http://examp.*.com')
        trace = filtr.process_trace([span])
        self.assertIsNone(trace)

    def test_is_not_match(self):
        span = Span(name='Name', tracer=None)
        span.set_tag(URL, r'http://anotherexample.com')
        filtr = FilterRequestsOnUrl('http://examp.*.com')
        trace = filtr.process_trace([span])
        self.assertIsNotNone(trace)

    def test_list_match(self):
        span = Span(name='Name', tracer=None)
        span.set_tag(URL, r'http://anotherdomain.example.com')
        filtr = FilterRequestsOnUrl([r'http://domain\.example\.com', r'http://anotherdomain\.example\.com'])
        trace = filtr.process_trace([span])
        self.assertIsNone(trace)

    def test_list_no_match(self):
        span = Span(name='Name', tracer=None)
        span.set_tag(URL, r'http://cooldomain.example.com')
        filtr = FilterRequestsOnUrl([r'http://domain\.example\.com', r'http://anotherdomain\.example\.com'])
        trace = filtr.process_trace([span])
        self.assertIsNotNone(trace)
