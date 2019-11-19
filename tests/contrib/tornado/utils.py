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

from tornado.testing import AsyncHTTPTestCase

from oteltrace.contrib.tornado import patch, unpatch
from oteltrace.compat import reload_module

from .web import app, compat
from ...base import BaseTracerTestCase


class TornadoTestCase(BaseTracerTestCase, AsyncHTTPTestCase):
    """
    Generic TornadoTestCase where the framework is globally patched
    and unpatched before/after each test. A dummy tracer is provided
    in the `self.tracer` attribute.
    """
    def get_app(self):
        # patch Tornado and reload module app
        patch()
        reload_module(compat)
        reload_module(app)

        settings = self.get_settings()
        trace_settings = settings.get('opentelemetry_trace', {})
        settings['opentelemetry_trace'] = trace_settings
        trace_settings['tracer'] = self.tracer
        self.app = app.make_app(settings=settings)
        return self.app

    def get_settings(self):
        # override settings in your TestCase
        return {}

    def tearDown(self):
        super(TornadoTestCase, self).tearDown()
        # unpatch Tornado
        unpatch()
        reload_module(compat)
        reload_module(app)
