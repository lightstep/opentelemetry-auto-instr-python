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

"""
OpenTelemetry trace code for flask_cache
"""

# stdlib
import logging

# project
from .utils import _extract_conn_tags, _resource_from_cache_prefix
from ...constants import ANALYTICS_SAMPLE_RATE_KEY
from ...settings import config

# 3rd party
from flask.ext.cache import Cache


log = logging.Logger(__name__)

TYPE = 'cache'
DEFAULT_SERVICE = 'flask-cache'

# standard tags
COMMAND_KEY = 'flask_cache.key'
CACHE_BACKEND = 'flask_cache.backend'
CONTACT_POINTS = 'flask_cache.contact_points'


def get_traced_cache(oteltracer, service=DEFAULT_SERVICE, meta=None):
    """
    Return a traced Cache object that behaves exactly as the ``flask.ext.cache.Cache class``
    """

    class TracedCache(Cache):
        """
        Traced cache backend that monitors any operations done by flask_cache. Observed actions are:
            * get, set, add, delete, clear
            * all many_ operations
        """
        _opentelemetry_tracer = oteltracer
        _opentelemetry_service = service
        _opentelemetry_meta = meta

        def __trace(self, cmd):
            """
            Start a tracing with default attributes and tags
            """
            # create a new span
            s = self._opentelemetry_tracer.trace(
                cmd,
                span_type=TYPE,
                service=self._opentelemetry_service
            )
            # set span tags
            s.set_tag(CACHE_BACKEND, self.config.get('CACHE_TYPE'))
            s.set_tags(self._opentelemetry_meta)
            # set analytics sample rate
            s.set_tag(
                ANALYTICS_SAMPLE_RATE_KEY,
                config.flask_cache.get_analytics_sample_rate()
            )
            # add connection meta if there is one
            if getattr(self.cache, '_client', None):
                try:
                    s.set_tags(_extract_conn_tags(self.cache._client))
                except Exception:
                    log.debug('error parsing connection tags', exc_info=True)

            return s

        def get(self, *args, **kwargs):
            """
            Track ``get`` operation
            """
            with self.__trace('flask_cache.cmd') as span:
                span.resource = _resource_from_cache_prefix('GET', self.config)
                if len(args) > 0:
                    span.set_tag(COMMAND_KEY, args[0])
                return super(TracedCache, self).get(*args, **kwargs)

        def set(self, *args, **kwargs):
            """
            Track ``set`` operation
            """
            with self.__trace('flask_cache.cmd') as span:
                span.resource = _resource_from_cache_prefix('SET', self.config)
                if len(args) > 0:
                    span.set_tag(COMMAND_KEY, args[0])
                return super(TracedCache, self).set(*args, **kwargs)

        def add(self, *args, **kwargs):
            """
            Track ``add`` operation
            """
            with self.__trace('flask_cache.cmd') as span:
                span.resource = _resource_from_cache_prefix('ADD', self.config)
                if len(args) > 0:
                    span.set_tag(COMMAND_KEY, args[0])
                return super(TracedCache, self).add(*args, **kwargs)

        def delete(self, *args, **kwargs):
            """
            Track ``delete`` operation
            """
            with self.__trace('flask_cache.cmd') as span:
                span.resource = _resource_from_cache_prefix('DELETE', self.config)
                if len(args) > 0:
                    span.set_tag(COMMAND_KEY, args[0])
                return super(TracedCache, self).delete(*args, **kwargs)

        def delete_many(self, *args, **kwargs):
            """
            Track ``delete_many`` operation
            """
            with self.__trace('flask_cache.cmd') as span:
                span.resource = _resource_from_cache_prefix('DELETE_MANY', self.config)
                span.set_tag(COMMAND_KEY, list(args))
                return super(TracedCache, self).delete_many(*args, **kwargs)

        def clear(self, *args, **kwargs):
            """
            Track ``clear`` operation
            """
            with self.__trace('flask_cache.cmd') as span:
                span.resource = _resource_from_cache_prefix('CLEAR', self.config)
                return super(TracedCache, self).clear(*args, **kwargs)

        def get_many(self, *args, **kwargs):
            """
            Track ``get_many`` operation
            """
            with self.__trace('flask_cache.cmd') as span:
                span.resource = _resource_from_cache_prefix('GET_MANY', self.config)
                span.set_tag(COMMAND_KEY, list(args))
                return super(TracedCache, self).get_many(*args, **kwargs)

        def set_many(self, *args, **kwargs):
            """
            Track ``set_many`` operation
            """
            with self.__trace('flask_cache.cmd') as span:
                span.resource = _resource_from_cache_prefix('SET_MANY', self.config)
                if len(args) > 0:
                    span.set_tag(COMMAND_KEY, list(args[0].keys()))
                return super(TracedCache, self).set_many(*args, **kwargs)

    return TracedCache
