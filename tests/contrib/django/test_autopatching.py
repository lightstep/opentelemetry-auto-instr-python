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

import django

from oteltrace.monkey import patch
from .utils import DjangoTraceTestCase
from django.conf import settings
from unittest import skipIf


class DjangoAutopatchTest(DjangoTraceTestCase):
    def setUp(self):
        super(DjangoAutopatchTest, self).setUp()
        patch(django=True)
        django.setup()

    @skipIf(django.VERSION >= (1, 10), 'skip if version above 1.10')
    def test_autopatching_middleware_classes(self):
        assert django._opentelemetry_patch
        assert 'oteltrace.contrib.django' in settings.INSTALLED_APPS
        assert settings.MIDDLEWARE_CLASSES[0] == 'oteltrace.contrib.django.TraceMiddleware'
        assert settings.MIDDLEWARE_CLASSES[-1] == 'oteltrace.contrib.django.TraceExceptionMiddleware'

    @skipIf(django.VERSION >= (1, 10), 'skip if version above 1.10')
    def test_autopatching_twice_middleware_classes(self):
        assert django._opentelemetry_patch
        # Call django.setup() twice and ensure we don't add a duplicate tracer
        django.setup()

        found_app = settings.INSTALLED_APPS.count('oteltrace.contrib.django')
        assert found_app == 1

        assert settings.MIDDLEWARE_CLASSES[0] == 'oteltrace.contrib.django.TraceMiddleware'
        assert settings.MIDDLEWARE_CLASSES[-1] == 'oteltrace.contrib.django.TraceExceptionMiddleware'

        found_mw = settings.MIDDLEWARE_CLASSES.count('oteltrace.contrib.django.TraceMiddleware')
        assert found_mw == 1
        found_mw = settings.MIDDLEWARE_CLASSES.count('oteltrace.contrib.django.TraceExceptionMiddleware')
        assert found_mw == 1

    @skipIf(django.VERSION < (1, 10), 'skip if version is below 1.10')
    def test_autopatching_middleware(self):
        assert django._opentelemetry_patch
        assert 'oteltrace.contrib.django' in settings.INSTALLED_APPS
        assert settings.MIDDLEWARE[0] == 'oteltrace.contrib.django.TraceMiddleware'
        # MIDDLEWARE_CLASSES gets created internally in django 1.10 & 1.11 but doesn't
        # exist at all in 2.0.
        assert not getattr(settings, 'MIDDLEWARE_CLASSES', None) or \
            'oteltrace.contrib.django.TraceMiddleware' \
            not in settings.MIDDLEWARE_CLASSES
        assert settings.MIDDLEWARE[-1] == 'oteltrace.contrib.django.TraceExceptionMiddleware'
        assert not getattr(settings, 'MIDDLEWARE_CLASSES', None) or \
            'oteltrace.contrib.django.TraceExceptionMiddleware' \
            not in settings.MIDDLEWARE_CLASSES

    @skipIf(django.VERSION < (1, 10), 'skip if version is below 1.10')
    def test_autopatching_twice_middleware(self):
        assert django._opentelemetry_patch
        # Call django.setup() twice and ensure we don't add a duplicate tracer
        django.setup()

        found_app = settings.INSTALLED_APPS.count('oteltrace.contrib.django')
        assert found_app == 1

        assert settings.MIDDLEWARE[0] == 'oteltrace.contrib.django.TraceMiddleware'
        # MIDDLEWARE_CLASSES gets created internally in django 1.10 & 1.11 but doesn't
        # exist at all in 2.0.
        assert not getattr(settings, 'MIDDLEWARE_CLASSES', None) or \
            'oteltrace.contrib.django.TraceMiddleware' \
            not in settings.MIDDLEWARE_CLASSES
        assert settings.MIDDLEWARE[-1] == 'oteltrace.contrib.django.TraceExceptionMiddleware'
        assert not getattr(settings, 'MIDDLEWARE_CLASSES', None) or \
            'oteltrace.contrib.django.TraceExceptionMiddleware' \
            not in settings.MIDDLEWARE_CLASSES

        found_mw = settings.MIDDLEWARE.count('oteltrace.contrib.django.TraceMiddleware')
        assert found_mw == 1

        found_mw = settings.MIDDLEWARE.count('oteltrace.contrib.django.TraceExceptionMiddleware')
        assert found_mw == 1


class DjangoAutopatchCustomMiddlewareTest(DjangoTraceTestCase):
    @skipIf(django.VERSION < (1, 10), 'skip if version is below 1.10')
    def test_autopatching_empty_middleware(self):
        with self.settings(MIDDLEWARE=[]):
            patch(django=True)
            django.setup()
        assert django._opentelemetry_patch
        assert 'oteltrace.contrib.django' in settings.INSTALLED_APPS
        assert settings.MIDDLEWARE[0] == 'oteltrace.contrib.django.TraceMiddleware'
        # MIDDLEWARE_CLASSES gets created internally in django 1.10 & 1.11 but doesn't
        # exist at all in 2.0.
        assert not getattr(settings, 'MIDDLEWARE_CLASSES', None) or \
            'oteltrace.contrib.django.TraceMiddleware' \
            not in settings.MIDDLEWARE_CLASSES
        assert settings.MIDDLEWARE[-1] == 'oteltrace.contrib.django.TraceExceptionMiddleware'
        assert not getattr(settings, 'MIDDLEWARE_CLASSES', None) or \
            'oteltrace.contrib.django.TraceExceptionMiddleware' \
            not in settings.MIDDLEWARE_CLASSES
