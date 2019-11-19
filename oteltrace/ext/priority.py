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

"""
Priority is a hint given to the backend so that it knows which traces to reject or kept.
In a distributed context, it should be set before any context propagation (fork, RPC calls) to be effective.

For example:

from oteltrace.ext.priority import USER_REJECT, USER_KEEP

context = tracer.context_provider.active()
# Indicate to not keep the trace
context.sampling_priority = USER_REJECT

# Indicate to keep the trace
span.context.sampling_priority = USER_KEEP
"""

# Use this to explicitly inform the backend that a trace should be rejected and not stored.
USER_REJECT = -1
# Used by the builtin sampler to inform the backend that a trace should be rejected and not stored.
AUTO_REJECT = 0
# Used by the builtin sampler to inform the backend that a trace should be kept and stored.
AUTO_KEEP = 1
# Use this to explicitly inform the backend that a trace should be kept and stored.
USER_KEEP = 2
