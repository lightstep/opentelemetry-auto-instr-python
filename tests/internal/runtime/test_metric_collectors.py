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

from oteltrace.internal.runtime.metric_collectors import (
    RuntimeMetricCollector,
    GCRuntimeMetricCollector,
    PSUtilRuntimeMetricCollector,
)

from oteltrace.internal.runtime.constants import (
    GC_COUNT_GEN0,
    GC_RUNTIME_METRICS,
    PSUTIL_RUNTIME_METRICS,
)
from ...base import BaseTestCase


class TestRuntimeMetricCollector(BaseTestCase):
    def test_failed_module_load_collect(self):
        """Attempts to collect from a collector when it has failed to load its
        module should return no metrics gracefully.
        """
        class A(RuntimeMetricCollector):
            required_modules = ['moduleshouldnotexist']

            def collect_fn(self, keys):
                return {'k': 'v'}

        self.assertIsNotNone(A().collect(), 'collect should return valid metrics')


class TestPSUtilRuntimeMetricCollector(BaseTestCase):
    def test_metrics(self):
        collector = PSUtilRuntimeMetricCollector()
        for (key, value) in collector.collect(PSUTIL_RUNTIME_METRICS):
            self.assertIsNotNone(value)


class TestGCRuntimeMetricCollector(BaseTestCase):
    def test_metrics(self):
        collector = GCRuntimeMetricCollector()
        for (key, value) in collector.collect(GC_RUNTIME_METRICS):
            self.assertIsNotNone(value)

    def test_gen1_changes(self):
        # disable gc
        import gc
        gc.disable()

        # start collector and get current gc counts
        collector = GCRuntimeMetricCollector()
        gc.collect()
        start = gc.get_count()

        # create reference
        a = []
        collected = collector.collect([GC_COUNT_GEN0])
        self.assertGreater(collected[0][1], start[0])

        # delete reference and collect
        del a
        gc.collect()
        collected_after = collector.collect([GC_COUNT_GEN0])
        assert len(collected_after) == 1
        assert collected_after[0][0] == 'runtime.python.gc.count.gen0'
        assert isinstance(collected_after[0][1], int)
