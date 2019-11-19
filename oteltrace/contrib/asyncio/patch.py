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

import asyncio

from oteltrace.vendor.wrapt import wrap_function_wrapper as _w

from ...internal.context_manager import CONTEXTVARS_IS_AVAILABLE
from .wrappers import wrapped_create_task, wrapped_create_task_contextvars
from ...utils.wrappers import unwrap as _u


def patch():
    """Patches current loop `create_task()` method to enable spawned tasks to
    parent to the base task context.
    """
    if getattr(asyncio, '_opentelemetry_patch', False):
        return
    setattr(asyncio, '_opentelemetry_patch', True)

    loop = asyncio.get_event_loop()
    if CONTEXTVARS_IS_AVAILABLE:
        _w(loop, 'create_task', wrapped_create_task_contextvars)
    else:
        _w(loop, 'create_task', wrapped_create_task)


def unpatch():
    """Remove tracing from patched modules."""

    if getattr(asyncio, '_opentelemetry_patch', False):
        setattr(asyncio, '_opentelemetry_patch', False)

    loop = asyncio.get_event_loop()
    _u(loop, 'create_task')
