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

from oteltrace.vendor.wrapt import wrap_function_wrapper as wrap

from rest_framework.views import APIView

from ...utils.wrappers import unwrap


def patch_restframework(tracer):
    """ Patches rest_framework app.

    To trace exceptions occuring during view processing we currently use a TraceExceptionMiddleware.
    However the rest_framework handles exceptions before they come to our middleware.
    So we need to manually patch the rest_framework exception handler
    to set the exception stack trace in the current span.

    """

    def _traced_handle_exception(wrapped, instance, args, kwargs):
        """ Sets the error message, error type and exception stack trace to the current span
            before calling the original exception handler.
        """
        span = tracer.current_span()
        if span is not None:
            span.set_traceback()

        return wrapped(*args, **kwargs)

    # do not patch if already patched
    if getattr(APIView, '_opentelemetry_patch', False):
        return
    else:
        setattr(APIView, '_opentelemetry_patch', True)

    # trace the handle_exception method
    wrap('rest_framework.views', 'APIView.handle_exception', _traced_handle_exception)


def unpatch_restframework():
    """ Unpatches rest_framework app."""
    if getattr(APIView, '_opentelemetry_patch', False):
        setattr(APIView, '_opentelemetry_patch', False)
        unwrap(APIView, 'handle_exception')
