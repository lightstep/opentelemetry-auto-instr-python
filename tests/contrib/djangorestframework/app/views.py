from django.conf.urls import url, include
from django.contrib.auth.models import User
from django.db import models

from rest_framework import viewsets, routers, serializers, mixins
from rest_framework.permissions import IsAuthenticated


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('url', 'username', 'email', 'groups')


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]


class SelfSerializer(serializers.ModelSerializer):
    groups = serializers.StringRelatedField(many=True)

    class Meta:
        model = User
        fields = ('email', 'groups')

class ErrorViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer

    def list(self, request):
        def my_err_func():
            raise Exception('Custom exception')
        my_err_func()

class SelfViewSet(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    serializer_class = SelfSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


router = routers.DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'error', ErrorViewSet)

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'self', SelfViewSet.as_view({'get':'retrieve'})),
    url(r'^', include(router.urls)),
]
