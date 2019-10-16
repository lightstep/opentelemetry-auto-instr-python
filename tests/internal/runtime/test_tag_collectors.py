from oteltrace.internal.runtime import constants
from oteltrace.internal.runtime import tag_collectors


def test_values():
    ptc = tag_collectors.PlatformTagCollector()
    values = dict(ptc.collect())
    assert constants.PLATFORM_TAGS == set(values.keys())
