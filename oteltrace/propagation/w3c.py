import re

from ..context import Context
from ..ext import priority

class W3CHTTPPropagator:
    """w3c compatible propagator"""
    _TRACEPARENT_HEADER_NAME = "traceparent"
    _TRACEPARENT_HEADER_FORMAT = (
        "^[ \t]*([0-9a-f]{2})-([0-9a-f]{32})-([0-9a-f]{16})-([0-9a-f]{2})(-.*)?[ \t]*$"
    )
    _TRACEPARENT_HEADER_FORMAT_RE = re.compile(_TRACEPARENT_HEADER_FORMAT)
    _SAMPLING_PRIORITY_MAP={
        priority.USER_REJECT:0,
        priority.AUTO_REJECT:0,
        priority.AUTO_KEEP:1,
        priority.USER_KEEP:1,
    }
    def inject(self, span_context, headers):
        # TODO: what should be a default value?
        sampled = 0
        if span_context.sampling_priority is not None:
            sampled = self._SAMPLING_PRIORITY_MAP[span_context.sampling_priority]

        traceparent_string = "00-{:032x}-{:016x}-{:02x}".format(
            span_context.trace_id, span_context.span_id, sampled
        )

        headers[self._TRACEPARENT_HEADER_NAME] = traceparent_string

    def extract(self, headers):
        if not headers:
            return Context()

        # TODO: lookup ignoring case
        header = headers.get(self._TRACEPARENT_HEADER_NAME)
        if not header:
            return Context()

        match = re.search(self._TRACEPARENT_HEADER_FORMAT_RE, header)
        if not match:
            return Context()

        version = match.group(1)
        trace_id_str = match.group(2)
        span_id_str = match.group(3)
        trace_options_str = match.group(4)

        if version == "00":
            if match.group(5):
                return Context()
        if version == "ff":
            return Context()

        trace_id=int(trace_id_str, 16)
        span_id=int(span_id_str, 16)
        trace_options=int(trace_options_str, 16)
        # TODO: probably not needed
        if trace_id == 0 or span_id == 0:
            return Context()

        # There is not a way to identify between USER and AUTO at this point,
        # just use AUTO.
        if trace_options & 0x1:
            sampling_priority = priority.AUTO_KEEP
        else:
            sampling_priority = priority.AUTO_REJECT

        return Context(
            trace_id=trace_id,
            span_id=span_id,
            sampling_priority=sampling_priority,
        )
