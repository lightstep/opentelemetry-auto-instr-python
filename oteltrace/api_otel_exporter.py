# project
from .internal.logger import get_logger

# opentelemetry
from opentelemetry import trace as trace_api
from opentelemetry.sdk import trace

log = get_logger(__name__)


class Response(object):
    """
    Custom API Response object to represent a response from calling the API.

    We do this to ensure we know expected properties will exist, and so we
    can call `resp.read()` and load the body once into an instance before we
    close the HTTPConnection used for the request.
    """

    def get_json(self):
        """Helper to parse the body of this request as JSON"""
        return None


class APIOtel(object):
    """
    Export data to OpenTelemetry using an SDK exporter
    """

    def __init__(self, exporter):
        self._exporter = exporter

    def send_traces(self, traces):
        """Send traces to the API.

        :param traces: A list of traces.
        :return: The list of API HTTP responses.
        """
        responses = []

        spans = []
        for tr in traces:
            for span in tr:
                spans.append(self._span_to_otel_span(span))
        self._exporter.export(spans)
        return responses

    def _span_to_otel_span(self, span):
        # create out-of-band span (it would be better to create a SpanView)

        # context for current span
        context = trace_api.SpanContext(
            trace_id=span.trace_id, span_id=span.span_id
        )

        # parent (if one is set)
        parent = None
        if span.parent_id is not None:
            parent = trace_api.SpanContext(
                trace_id=span.trace_id, span_id=span.parent_id
            )

        # attributes
        attributes = {}
        # ddog members to opentelemetry attributes.
        # https://github.com/DataDog/dd-trace-py/blob/1f04d0fcfb3974611967004a22882b55db77433e/oteltrace/opentracer/span.py#L113
        # TODO: use constants
        if span.span_type is not None:
            # TODO(Mauricio): OpenTracing maps to 'span.type', I think
            # component is the right one for OpenTelemetry
            attributes['component'] = span.span_type

        if span.service is not None:
            attributes['service.name'] = span.service

        if span.resource is not None:
            attributes['resource.name'] = span.resource

        if span.context.sampling_priority is not None:
            attributes['sampling.priority'] = span.context.sampling_priority

        # tags
        for tag in span.meta.items():
            key = tag[0]
            value = tag[1]

            if key == 'out.host':
                key = 'peer.hostname'
            elif key == 'out.port':
                key = 'peer.port'

            attributes[key] = value

        # build span with all that info
        otel_span = trace.Span(
            name=span.name,
            context=context,
            parent=parent,
            attributes=attributes
            # TODO: attributes, events? links?
        )

        otel_span.start_time = int(span.start * 10**9)
        otel_span.end_time = int((span.start + span.duration) * 10**9)

        return otel_span
