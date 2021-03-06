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

from celery import signals

from oteltrace import Pin, config
from oteltrace.pin import _OTEL_PIN_NAME
from oteltrace.ext import AppTypes

from .constants import APP
from .signals import (
    trace_prerun,
    trace_postrun,
    trace_before_publish,
    trace_after_publish,
    trace_failure,
    trace_retry,
)


def patch_app(app, pin=None):
    """Attach the Pin class to the application and connect
    our handlers to Celery signals.
    """
    if getattr(app, '__opentelemetry_patch', False):
        return
    setattr(app, '__opentelemetry_patch', True)

    # attach the PIN object
    pin = pin or Pin(
        service=config.celery['worker_service_name'],
        app=APP,
        app_type=AppTypes.worker,
        _config=config.celery,
    )
    pin.onto(app)
    # connect to the Signal framework
    signals.task_prerun.connect(trace_prerun)
    signals.task_postrun.connect(trace_postrun)
    signals.before_task_publish.connect(trace_before_publish)
    signals.after_task_publish.connect(trace_after_publish)
    signals.task_failure.connect(trace_failure)
    signals.task_retry.connect(trace_retry)
    return app


def unpatch_app(app):
    """Remove the Pin instance from the application and disconnect
    our handlers from Celery signal framework.
    """
    if not getattr(app, '__opentelemetry_patch', False):
        return
    setattr(app, '__opentelemetry_patch', False)

    pin = Pin.get_from(app)
    if pin is not None:
        delattr(app, _OTEL_PIN_NAME)

    signals.task_prerun.disconnect(trace_prerun)
    signals.task_postrun.disconnect(trace_postrun)
    signals.before_task_publish.disconnect(trace_before_publish)
    signals.after_task_publish.disconnect(trace_after_publish)
    signals.task_failure.disconnect(trace_failure)
    signals.task_retry.disconnect(trace_retry)
