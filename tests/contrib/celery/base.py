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

from celery import Celery

from oteltrace import Pin
from oteltrace.compat import PY2
from oteltrace.contrib.celery import patch, unpatch

from ..config import REDIS_CONFIG
from ...base import BaseTracerTestCase


REDIS_URL = 'redis://127.0.0.1:{port}'.format(port=REDIS_CONFIG['port'])
BROKER_URL = '{redis}/{db}'.format(redis=REDIS_URL, db=0)
BACKEND_URL = '{redis}/{db}'.format(redis=REDIS_URL, db=1)


class CeleryBaseTestCase(BaseTracerTestCase):
    """Test case that handles a full fledged Celery application with a
    custom tracer. It patches the new Celery application.
    """

    def setUp(self):
        super(CeleryBaseTestCase, self).setUp()

        # instrument Celery and create an app with Broker and Result backends
        patch()
        self.pin = Pin(service='celery-unittest', tracer=self.tracer)
        self.app = Celery('celery.test_app', broker=BROKER_URL, backend=BACKEND_URL)
        # override pins to use our Dummy Tracer
        Pin.override(self.app, tracer=self.tracer)

    def tearDown(self):
        # remove instrumentation from Celery
        unpatch()
        self.app = None

        super(CeleryBaseTestCase, self).tearDown()

    def assert_items_equal(self, a, b):
        if PY2:
            return self.assertItemsEqual(a, b)
        return self.assertCountEqual(a, b)
