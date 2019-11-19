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

from unittest import TestCase, mock

from oteltrace.propagation import http as http_propagator_module
from oteltrace.propagation.http import DatadogHTTPPropagator

from oteltrace import tracer


class TestHTTPPropagator(TestCase):
    def test_default(self):
        prop = http_propagator_module.HTTPPropagator()
        self.assertIsInstance(prop, DatadogHTTPPropagator)

    def test_set_http_propagator_factory(self):
        mock_propagator = mock.Mock()

        def get_propagator():
            return mock_propagator

        http_propagator_module.set_http_propagator_factory(get_propagator)

        self.assertIs(http_propagator_module.HTTPPropagator(), mock_propagator)

    def test_tracer_configure_http_propagator(self):
        mock_propagator = mock.Mock()

        def get_propagator():
            return mock_propagator

        tracer.configure(http_propagator=get_propagator)

        self.assertIs(http_propagator_module.HTTPPropagator(), mock_propagator)
