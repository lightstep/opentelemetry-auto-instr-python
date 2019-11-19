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

from oteltrace import Pin
from oteltrace.contrib.flask import patch, unpatch
import flask
from oteltrace.vendor import wrapt

from ...base import BaseTracerTestCase


class BaseFlaskTestCase(BaseTracerTestCase):
    def setUp(self):
        super(BaseFlaskTestCase, self).setUp()

        patch()

        self.app = flask.Flask(__name__, template_folder='test_templates/')
        self.client = self.app.test_client()
        Pin.override(self.app, tracer=self.tracer)

    def tearDown(self):
        # Remove any remaining spans
        self.tracer.writer.pop()

        # Unpatch Flask
        unpatch()

    def get_spans(self):
        return self.tracer.writer.pop()

    def assert_is_wrapped(self, obj):
        self.assertTrue(isinstance(obj, wrapt.ObjectProxy), '{} is not wrapped'.format(obj))

    def assert_is_not_wrapped(self, obj):
        self.assertFalse(isinstance(obj, wrapt.ObjectProxy), '{} is wrapped'.format(obj))

    def find_span_by_name(self, spans, name, required=True):
        """Helper to find the first span with a given name from a list"""
        span = next((s for s in spans if s.name == name), None)
        if required:
            self.assertIsNotNone(span, 'could not find span with name {}'.format(name))
        return span

    def find_span_parent(self, spans, span, required=True):
        """Helper to search for a span's parent in a given list of spans"""
        parent = next((s for s in spans if s.span_id == span.parent_id), None)
        if required:
            self.assertIsNotNone(parent, 'could not find parent span {}'.format(span))
        return parent
