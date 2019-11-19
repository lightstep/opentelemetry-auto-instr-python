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

import oteltrace


def get_correlation_ids(tracer=None):
    """Retrieves the Correlation Identifiers for the current active ``Trace``.
    This helper method can be achieved manually and should be considered
    only a shortcut. The main reason is to abstract the current ``Tracer``
    implementation so that these identifiers can be extracted either the
    tracer is an OpenTracing tracer or a OpenTelemetry tracer.

    OpenTracing users can still extract these values using the ``ScopeManager``
    API, though this shortcut is a simple one-liner. The usage is:

        from oteltrace import helpers

        trace_id, span_id = helpers.get_correlation_ids()

    :returns: a tuple containing the trace_id and span_id
    """
    # Consideration: currently we don't have another way to "define" a
    # GlobalTracer. In the case of OpenTracing, ``opentracing.tracer`` is exposed
    # and we're doing the same here for ``oteltrace.tracer``. Because this helper
    # must work also with OpenTracing, we should take the right used ``Tracer``.
    # At the time of writing, it's enough to support our OpenTelemetry Tracer.

    # If no tracer passed in, use global tracer
    if not tracer:
        tracer = oteltrace.tracer

    # If tracer is disabled, skip
    if not tracer.enabled:
        return None, None

    span = tracer.current_span()
    if not span:
        return None, None
    return span.trace_id, span.span_id
