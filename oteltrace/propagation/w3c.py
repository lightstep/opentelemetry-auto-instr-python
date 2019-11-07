import re

from ..context import Context
from ..ext import priority


_KEY_WITHOUT_VENDOR_FORMAT = r'[a-z][_0-9a-z\-\*\/]{0,255}'
_KEY_WITH_VENDOR_FORMAT = (
    r'[a-z][_0-9a-z\-\*\/]{0,240}@[a-z][_0-9a-z\-\*\/]{0,13}'
)

_KEY_FORMAT = _KEY_WITHOUT_VENDOR_FORMAT + '|' + _KEY_WITH_VENDOR_FORMAT
_VALUE_FORMAT = (
    r'[\x20-\x2b\x2d-\x3c\x3e-\x7e]{0,255}[\x21-\x2b\x2d-\x3c\x3e-\x7e]'
)

_DELIMITER_FORMAT = '[ \t]*,[ \t]*'
_MEMBER_FORMAT = '({})(=)({})[ \t]*'.format(_KEY_FORMAT, _VALUE_FORMAT)

_DELIMITER_FORMAT_RE = re.compile(_DELIMITER_FORMAT)
_MEMBER_FORMAT_RE = re.compile(_MEMBER_FORMAT)

_TRACECONTEXT_MAXIMUM_TRACESTATE_KEYS = 32


class W3CHTTPPropagator:
    """w3c compatible propagator"""
    _TRACEPARENT_HEADER_NAME = 'traceparent'
    _TRACESTATE_HEADER_NAME = 'tracestate'
    _TRACEPARENT_HEADER_FORMAT = (
        '^[ \t]*([0-9a-f]{2})-([0-9a-f]{32})-([0-9a-f]{16})-([0-9a-f]{2})(-.*)?[ \t]*$'
    )
    _TRACEPARENT_HEADER_FORMAT_RE = re.compile(_TRACEPARENT_HEADER_FORMAT)
    _SAMPLING_PRIORITY_MAP = {
        priority.USER_REJECT: 0,
        priority.AUTO_REJECT: 0,
        priority.AUTO_KEEP: 1,
        priority.USER_KEEP: 1,
    }

    def inject(self, span_context, headers):
        # TODO: what should be a default value?
        sampled = 0
        if span_context.sampling_priority is not None:
            sampled = self._SAMPLING_PRIORITY_MAP[span_context.sampling_priority]

        traceparent_string = '00-{:032x}-{:016x}-{:02x}'.format(
            span_context.trace_id, span_context.span_id, sampled
        )

        headers[self._TRACEPARENT_HEADER_NAME] = traceparent_string
        # is there is state in the context propagate it
        if hasattr(span_context, 'tracestate'):
            tracestate_string = _format_tracestate(span_context.tracestate)
            headers[self._TRACESTATE_HEADER_NAME] = tracestate_string

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

        if version == '00':
            if match.group(5):
                return Context()
        if version == 'ff':
            return Context()

        trace_id = int(trace_id_str, 16)
        span_id = int(span_id_str, 16)
        trace_options = int(trace_options_str, 16)
        if trace_id == 0 or span_id == 0:
            return Context()

        # There is not a way to identify between USER and AUTO at this point,
        # just use AUTO.
        if trace_options & 0x1:
            sampling_priority = priority.AUTO_KEEP
        else:
            sampling_priority = priority.AUTO_REJECT

        tracestate_header = headers.get(self._TRACESTATE_HEADER_NAME)
        tracestate = _parse_tracestate(tracestate_header)

        ctx = Context(
            trace_id=trace_id,
            span_id=span_id,
            sampling_priority=sampling_priority,
        )

        ctx.tracestate = tracestate

        return ctx


def _parse_tracestate(header):
    """Parse one or more w3c tracestate header into a TraceState.

    Args:
        string: the value of the tracestate header.

    Returns:
        A valid TraceState that contains values extracted from
        the tracestate header.

        If the format of one headers is illegal, all values will
        be discarded and an empty tracestate will be returned.

        If the number of keys is beyond the maximum, all values
        will be discarded and an empty tracestate will be returned.
    """
    tracestate = {}
    value_count = 0

    if header is None:
        return {}
    for member in re.split(_DELIMITER_FORMAT_RE, header):
        # empty members are valid, but no need to process further.
        if not member:
            continue
        match = _MEMBER_FORMAT_RE.fullmatch(member)
        if not match:
            # TODO: log this?
            return {}
        key, _eq, value = match.groups()
        if key in tracestate:  # pylint:disable=E1135
            # duplicate keys are not legal in
            # the header, so we will remove
            return {}
        tracestate[key] = value
        value_count += 1
        if value_count > _TRACECONTEXT_MAXIMUM_TRACESTATE_KEYS:
            return {}
    return tracestate


def _format_tracestate(tracestate):
    """Parse a w3c tracestate header into a TraceState.

    Args:
        tracestate: the tracestate header to write

    Returns:
        A string that adheres to the w3c tracestate
        header format.
    """
    return ','.join(key + '=' + value for key, value in tracestate.items())
