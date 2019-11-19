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

# 3rd party
from django.apps import AppConfig, apps

# project
from .patch import apply_django_patches


class TracerConfig(AppConfig):
    name = 'oteltrace.contrib.django'
    label = 'opentelemetry_django'

    def ready(self):
        """
        Ready is called as soon as the registry is fully populated.
        Tracing capabilities must be enabled in this function so that
        all Django internals are properly configured.
        """
        rest_framework_is_installed = apps.is_installed('rest_framework')
        apply_django_patches(patch_rest_framework=rest_framework_is_installed)
