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

import oteltrace

from ...base import BaseTracerTestCase
from .app import get_app
from .test_suite import FalconTestCase


class AutoPatchTestCase(BaseTracerTestCase, testing.TestCase, FalconTestCase):

    # Added because falcon 1.3 and 1.4 test clients (falcon.testing.client.TestClient) expect this property to be
    # defined. It would be initialized in the constructor, but we call it here like in 'TestClient.__init__(self, None)'
    # because falcon 1.0.x does not have such module and would fail. Once we stop supporting falcon 1.0.x then we can
    # use the cleaner __init__ invocation
    _default_headers = None

    def setUp(self):
        super(AutoPatchTestCase, self).setUp()

        self._service = 'my-falcon'

        # Since most integrations do `from oteltrace import tracer` we cannot update do `oteltrace.tracer = self.tracer`
        self.original_writer = oteltrace.tracer.writer
        oteltrace.tracer.writer = self.tracer.writer
        self.tracer = oteltrace.tracer

        # build a test app without adding a tracer middleware;
        # reconfigure the global tracer since the autopatch mode
        # uses it
        self.api = get_app(tracer=None)

    def tearDown(self):
        super(AutoPatchTestCase, self).tearDown()

        oteltrace.tracer.writer = self.original_writer
