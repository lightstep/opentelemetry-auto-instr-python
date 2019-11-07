from oteltrace.internal.runtime.runtime_metrics import (
    RuntimeTags,
    RuntimeMetrics,
)
from oteltrace.internal.runtime.constants import (
    DEFAULT_RUNTIME_METRICS,
    GC_COUNT_GEN0,
    SERVICE,
    ENV
)

from ...base import (
    BaseTestCase,
    BaseTracerTestCase,
)


class TestRuntimeTags(BaseTracerTestCase):
    def test_all_tags(self):
        with self.override_global_tracer():
            with self.trace('test', service='test'):
                tags = set([k for (k, v) in RuntimeTags()])
                assert SERVICE in tags
                # no env set by default
                assert ENV not in tags

    def test_one_tag(self):
        with self.override_global_tracer():
            with self.trace('test', service='test'):
                tags = [k for (k, v) in RuntimeTags(enabled=[SERVICE])]
                self.assertEqual(tags, [SERVICE])

    def test_env_tag(self):
        def filter_only_env_tags(tags):
            return [
                (k, v)
                for (k, v) in RuntimeTags()
                if k == 'env'
            ]

        with self.override_global_tracer():
            # first without env tag set in tracer
            with self.trace('first-test', service='test'):
                tags = filter_only_env_tags(RuntimeTags())
                assert tags == []

            # then with an env tag set
            self.tracer.set_tags({'env': 'tests.dog'})
            with self.trace('second-test', service='test'):
                tags = filter_only_env_tags(RuntimeTags())
                assert tags == [('env', 'tests.dog')]

            # check whether updating env works
            self.tracer.set_tags({'env': 'staging.dog'})
            with self.trace('third-test', service='test'):
                tags = filter_only_env_tags(RuntimeTags())
                assert tags == [('env', 'staging.dog')]


class TestRuntimeMetrics(BaseTestCase):
    def test_all_metrics(self):
        metrics = set([k for (k, v) in RuntimeMetrics()])
        self.assertSetEqual(metrics, DEFAULT_RUNTIME_METRICS)

    def test_one_metric(self):
        metrics = [k for (k, v) in RuntimeMetrics(enabled=[GC_COUNT_GEN0])]
        self.assertEqual(metrics, [GC_COUNT_GEN0])
