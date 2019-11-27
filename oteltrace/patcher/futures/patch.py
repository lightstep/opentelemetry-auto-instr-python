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

from concurrent import futures

from oteltrace.vendor.wrapt import wrap_function_wrapper as _w

from .threading import _wrap_submit
from ...utils.wrappers import unwrap as _u


def patch():
    """Enables Context Propagation between threads"""
    if getattr(futures, '__opentelemetry_patch', False):
        return
    setattr(futures, '__opentelemetry_patch', True)

    _w('concurrent.futures', 'ThreadPoolExecutor.submit', _wrap_submit)


def unpatch():
    """Disables Context Propagation between threads"""
    if not getattr(futures, '__opentelemetry_patch', False):
        return
    setattr(futures, '__opentelemetry_patch', False)

    _u(futures.ThreadPoolExecutor, 'submit')
