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

from .app import patch_app

from ...utils.deprecation import deprecation


def patch_task(task, pin=None):
    """Deprecated API. The new API uses signals that can be activated via
    patch(celery=True) or through `oteltrace-run` script. Using this API
    enables instrumentation on all tasks.
    """
    deprecation(
        name='oteltrace.contrib.celery.patch_task',
        message='Use `patch(celery=True)` or `oteltrace-run` script instead',
        version='1.0.0',
    )

    # Enable instrumentation everywhere
    patch_app(task.app)
    return task


def unpatch_task(task):
    """Deprecated API. The new API uses signals that can be deactivated
    via unpatch() API. This API is now a no-op implementation so it doesn't
    affect instrumented tasks.
    """
    deprecation(
        name='oteltrace.contrib.celery.patch_task',
        message='Use `unpatch()` instead',
        version='1.0.0',
    )
    return task
