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

import logging

from oteltrace import config

from ...helpers import get_correlation_ids
from ...utils.wrappers import unwrap as _u
from ...vendor.wrapt import wrap_function_wrapper as _w

RECORD_ATTR_TRACE_ID = 'otel.trace_id'
RECORD_ATTR_SPAN_ID = 'otel.span_id'
RECORD_ATTR_VALUE_NULL = 0

config._add('logging', dict(
    tracer=None,  # by default, override here for custom tracer
))


def _w_makeRecord(func, instance, args, kwargs):
    record = func(*args, **kwargs)

    # add correlation identifiers to LogRecord
    trace_id, span_id = get_correlation_ids(tracer=config.logging.tracer)
    if trace_id and span_id:
        setattr(record, RECORD_ATTR_TRACE_ID, trace_id)
        setattr(record, RECORD_ATTR_SPAN_ID, span_id)
    else:
        setattr(record, RECORD_ATTR_TRACE_ID, RECORD_ATTR_VALUE_NULL)
        setattr(record, RECORD_ATTR_SPAN_ID, RECORD_ATTR_VALUE_NULL)

    return record


def patch():
    """
    Patch ``logging`` module in the Python Standard Library for injection of
    tracer information by wrapping the base factory method ``Logger.makeRecord``
    """
    if getattr(logging, '_opentelemetry_patch', False):
        return
    setattr(logging, '_opentelemetry_patch', True)

    _w(logging.Logger, 'makeRecord', _w_makeRecord)


def unpatch():
    if getattr(logging, '_opentelemetry_patch', False):
        setattr(logging, '_opentelemetry_patch', False)

        _u(logging.Logger, 'makeRecord')
