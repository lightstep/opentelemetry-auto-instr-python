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

import warnings
import unittest

from celery import Celery

from oteltrace.contrib.celery import patch_task, unpatch_task, unpatch


class CeleryDeprecatedTaskPatch(unittest.TestCase):
    """Ensures that the previous Task instrumentation is available
    as Deprecated API.
    """
    def setUp(self):
        # create a not instrumented Celery App
        self.app = Celery('celery.test_app')

    def tearDown(self):
        # be sure the system is always unpatched
        unpatch()
        self.app = None

    def test_patch_signals_connect(self):
        # calling `patch_task` enables instrumentation globally
        # while raising a Deprecation warning
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter('always')

            @patch_task
            @self.app.task
            def fn_task():
                return 42

            assert len(w) == 1
            assert issubclass(w[-1].category, DeprecationWarning)
            assert 'patch(celery=True)' in str(w[-1].message)

    def test_unpatch_signals_diconnect(self):
        # calling `unpatch_task` is a no-op that raises a Deprecation
        # warning
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter('always')

            @unpatch_task
            @self.app.task
            def fn_task():
                return 42

            assert len(w) == 1
            assert issubclass(w[-1].category, DeprecationWarning)
            assert 'unpatch()' in str(w[-1].message)
