from redis import StrictRedis

from ...utils.deprecation import deprecated


DEFAULT_SERVICE = 'redis'


@deprecated(message='Use patching instead (see the docs).', version='1.0.0')
def get_traced_redis(oteltracer, service=DEFAULT_SERVICE, meta=None):
    return _get_traced_redis(oteltracer, StrictRedis, service, meta)


@deprecated(message='Use patching instead (see the docs).', version='1.0.0')
def get_traced_redis_from(oteltracer, baseclass, service=DEFAULT_SERVICE, meta=None):
    return _get_traced_redis(oteltracer, baseclass, service, meta)


def _get_traced_redis(oteltracer, baseclass, service, meta):
    return baseclass
