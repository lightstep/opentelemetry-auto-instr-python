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
