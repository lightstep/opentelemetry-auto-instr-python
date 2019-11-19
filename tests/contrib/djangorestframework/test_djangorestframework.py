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
from django.apps import apps
from unittest import skipIf

from tests.contrib.django.utils import DjangoTraceTestCase


@skipIf(django.VERSION < (1, 10), 'requires django version >= 1.10')
class RestFrameworkTest(DjangoTraceTestCase):
    def setUp(self):
        super(RestFrameworkTest, self).setUp()

        # would raise an exception
        from rest_framework.views import APIView
        from oteltrace.contrib.django.restframework import unpatch_restframework

        self.APIView = APIView
        self.unpatch_restframework = unpatch_restframework

    def test_setup(self):
        assert apps.is_installed('rest_framework')
        assert hasattr(self.APIView, '_opentelemetry_patch')

    def test_unpatch(self):
        self.unpatch_restframework()
        assert not getattr(self.APIView, '_opentelemetry_patch')

        response = self.client.get('/users/')

        # Our custom exception handler is setting the status code to 500
        assert response.status_code == 500

        # check for spans
        spans = self.tracer.writer.pop()
        assert len(spans) == 1
        sp = spans[0]
        assert sp.name == 'django.request'
        assert sp.resource == 'tests.contrib.djangorestframework.app.views.UserViewSet'
        assert sp.error == 0
        assert sp.span_type == 'http'
        assert sp.get_tag('http.status_code') == '500'
        assert sp.get_tag('error.msg') is None

    def test_trace_exceptions(self):
        response = self.client.get('/users/')

        # Our custom exception handler is setting the status code to 500
        assert response.status_code == 500

        # check for spans
        spans = self.tracer.writer.pop()
        assert len(spans) == 1
        sp = spans[0]
        assert sp.name == 'django.request'
        assert sp.resource == 'tests.contrib.djangorestframework.app.views.UserViewSet'
        assert sp.error == 1
        assert sp.span_type == 'http'
        assert sp.get_tag('http.method') == 'GET'
        assert sp.get_tag('http.status_code') == '500'
        assert sp.get_tag('error.msg') == 'Authentication credentials were not provided.'
        assert 'NotAuthenticated' in sp.get_tag('error.stack')
