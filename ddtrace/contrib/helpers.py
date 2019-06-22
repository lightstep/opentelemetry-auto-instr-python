import functools

from ..internal.packages import (
    marker_passes,
    parse_marker,

    requirement_passes,
    parse_requirement,
)


class ConditionalContextDecorator:
    class ConditionFails(Exception):
        pass

    def condition_passes(self):
        raise NotImplementedError('ConditionalContextDecorator.condition_passes must be overriden by child class')

    def __call__(self, func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if self.condition_passes():
                return func(*args, **kwargs)
        return wrapper

    def __enter__(self):
        return self.condition_passes()

    def __exit__(self, *args, **kwargs):
        pass


class require_package(ConditionalContextDecorator):
    __slots__ = ('req', 'passes')

    def __init__(self, req):
        self.req = parse_requirement(req)
        self.passes = None

    def condition_passes(self):
        if self.passes is None:
            self.passes = requirement_passes(self.req)
        return self.passes


class require_marker(ConditionalContextDecorator):
    __slots__ = ('m', 'passes')

    def __init__(self, m):
        self.m = parse_marker(m)
        self.passes = None

    def condition_passes(self):
        if self.passes is None:
            self.passes = marker_passes(self.m)
        return self.passes
