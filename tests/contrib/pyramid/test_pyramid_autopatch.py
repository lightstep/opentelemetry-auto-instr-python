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

from pyramid.config import Configurator

from .test_pyramid import PyramidTestCase, PyramidBase


class TestPyramidAutopatch(PyramidTestCase):
    instrument = False


class TestPyramidExplicitTweens(PyramidTestCase):
    instrument = False

    def get_settings(self):
        return {
            'pyramid.tweens': 'pyramid.tweens.excview_tween_factory\n',
        }


class TestPyramidDistributedTracing(PyramidBase):
    instrument = False

    def test_distributed_tracing(self):
        # ensure the Context is properly created
        # if distributed tracing is enabled
        headers = {
            'x-datadog-trace-id': '100',
            'x-datadog-parent-id': '42',
            'x-datadog-sampling-priority': '2',
            'x-datadog-origin': 'synthetics',
        }
        self.app.get('/', headers=headers, status=200)
        writer = self.tracer.writer
        spans = writer.pop()
        assert len(spans) == 1
        # check the propagated Context
        span = spans[0]
        assert span.trace_id == 100
        assert span.parent_id == 42
        assert span.get_metric('_sampling_priority_v1') == 2


def _include_me(config):
    pass


def test_config_include():
    """ This test makes sure that relative imports still work when the
    application is run with oteltrace-run """
    config = Configurator()
    config.include('tests.contrib.pyramid._include_me')
