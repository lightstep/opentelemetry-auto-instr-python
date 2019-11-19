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


if django.VERSION >= (1, 10, 1):
    from django.urls import get_resolver

    def user_is_authenticated(user):
        # Explicit comparison due to the following bug
        # https://code.djangoproject.com/ticket/26988
        return user.is_authenticated == True  # noqa E712
else:
    from django.conf import settings
    from django.core import urlresolvers

    def user_is_authenticated(user):
        return user.is_authenticated()

    if django.VERSION >= (1, 9, 0):
        def get_resolver(urlconf=None):
            urlconf = urlconf or settings.ROOT_URLCONF
            urlresolvers.set_urlconf(urlconf)
            return urlresolvers.get_resolver(urlconf)
    else:
        def get_resolver(urlconf=None):
            urlconf = urlconf or settings.ROOT_URLCONF
            urlresolvers.set_urlconf(urlconf)
            return urlresolvers.RegexURLResolver(r'^/', urlconf)
