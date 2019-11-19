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

import celery

from oteltrace import Pin
from oteltrace.contrib.celery import unpatch_app

from .base import CeleryBaseTestCase


class CeleryAppTest(CeleryBaseTestCase):
    """Ensures the default application is properly instrumented"""

    def test_patch_app(self):
        # When celery.App is patched it must include a `Pin` instance
        app = celery.Celery()
        assert Pin.get_from(app) is not None

    def test_unpatch_app(self):
        # When celery.App is unpatched it must not include a `Pin` instance
        unpatch_app(celery.Celery)
        app = celery.Celery()
        assert Pin.get_from(app) is None
