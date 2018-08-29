import django
from django.apps import apps
from nose.tools import ok_, eq_
from unittest import skipIf

from tests.contrib.django.utils import DjangoTraceTestCase

@skipIf(django.VERSION < (1, 10), 'requires django version >= 1.10')
class RestFrameworkTest(DjangoTraceTestCase):
    def setUp(self):
        super(RestFrameworkTest, self).setUp()

        # would raise an exception
        from rest_framework.views import APIView
        from ddtrace.contrib.django.restframework import unpatch_restframework

        self.APIView = APIView
        self.unpatch_restframework = unpatch_restframework

    def test_setup(self):
        ok_(apps.is_installed('rest_framework'))
        ok_(hasattr(self.APIView, '_datadog_patch'))

    def test_unpatch(self):
        self.unpatch_restframework()
        ok_(not getattr(self.APIView, '_datadog_patch'))

        response = self.client.get('/users/')

        eq_(response.status_code, 403)

        # check for spans
        spans = self.tracer.writer.pop()
        eq_(len(spans), 1)
        sp = spans[0]
        eq_(sp.name, 'django.request')
        eq_(sp.resource, 'app.views.UserViewSet')
        eq_(sp.error, 0)
        eq_(sp.span_type, 'http')
        eq_(sp.get_tag('http.status_code'), '403')
        eq_(sp.get_tag('error.msg'), None)

    def test_trace_exceptions(self):
        response = self.client.get('/error/')

        # Our custom exception handler is setting the status code to 500
        eq_(response.status_code, 500)

        # check for spans
        spans = self.tracer.writer.pop()
        eq_(len(spans), 1)
        sp = spans[0]
        eq_(sp.name, 'django.request')
        eq_(sp.resource, 'app.views.ErrorViewSet')
        eq_(sp.error, 1)
        eq_(sp.span_type, 'http')
        eq_(sp.get_tag('http.method'), 'GET')
        eq_(sp.get_tag('http.status_code'), '500')
        eq_(sp.get_tag('error.msg'), 'Custom exception')
        ok_('my_err_func' in sp.get_tag('error.stack'))

    def test_get_request_no_auth(self):
        from rest_framework.test import APIClient

        client = APIClient()
        response = client.get('/self/')
        eq_(response.status_code, 403)

        # check for spans
        spans = self.tracer.writer.pop()
        eq_(len(spans), 1)
        sp = spans[0]
        eq_(sp.name, 'django.request')
        eq_(sp.resource, 'app.views.SelfViewSet')
        eq_(sp.error, 0)
        eq_(sp.span_type, 'http')
        # user auth'd so should fail
        eq_(sp.get_tag('http.status_code'), '403')
        eq_(sp.get_tag('error.msg'), None)

    def test_get_request_auth(self):
        from rest_framework.test import APIClient
        from django.contrib.auth import get_user_model

        UserModel = get_user_model()
        user = UserModel.objects.create_user(username='test', password='123')

        client = APIClient()
        client.force_authenticate(user=user)
        response = client.get('/self/')
        eq_(response.status_code, 200)
        # check for spans
        spans = self.tracer.writer.pop()
        eq_(len(spans), 3)
        sp = spans[1]
        eq_(sp.name, 'django.request')
        eq_(sp.resource, 'app.views.SelfViewSet')
        eq_(sp.error, 0)
        eq_(sp.span_type, 'http')
        # user is auth'd so should succeed
        eq_(sp.get_tag('http.status_code'), '200')
        eq_(sp.get_tag('error.msg'), None)

    def test_options_request(self):
        from rest_framework.test import APIClient

        client = APIClient()
        response = client.options('/self/')

        eq_(response.status_code, 403)

        # check for spans
        spans = self.tracer.writer.pop()
        eq_(len(spans), 1)
        sp = spans[0]
        eq_(sp.name, 'django.request')
        eq_(sp.resource, 'app.views.SelfViewSet')
        eq_(sp.error, 0)
        eq_(sp.span_type, 'http')
        eq_(sp.get_tag('http.status_code'), '403')
        eq_(sp.get_tag('error.msg'), None)
