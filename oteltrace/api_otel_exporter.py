# stdlib
import os
import time
import oteltrace
import socket
import importlib

# project
from .internal.logger import get_logger

# opentelemetry
from opentelemetry import trace as trace_api
from opentelemetry.sdk import trace
from opentelemetry.sdk.trace import export

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

OTEL_MODULE='OTEL_EXPORTER_MODULE'
OTEL_FACTORY='OTEL_EXPORTER_FACTORY'
OTEL_OPT_PREFIX='OTEL_EXPORTER_OPTIONS_'

def get_otel_exporter_options():
    ops = {}

    for var in os.environ:
        if var.startswith(OTEL_OPT_PREFIX):
            opt_name = var[len(OTEL_OPT_PREFIX):]
            ops[opt_name] = os.environ.get(var)

    return ops

def load_exporter():
    exporter_module = os.environ.get(OTEL_MODULE)
    if exporter_module is None:
        log.error('%s is not defined.', OTEL_MODULE)
        return None

    exporter_type = os.environ.get(OTEL_FACTORY)
    if exporter_type is None:
        log.error('%s is not defined.', OTEL_FACTORY)
        return None

    try:
        otel_module = importlib.import_module(exporter_module)
        otel_callback =  getattr(otel_module, exporter_type)
        opt = get_otel_exporter_options()
        return otel_callback(**opt)
    except (ImportError, SyntaxError, AttributeError):
        log.exception('Error creating exporter instance.')
        return None


class APIOtel(object):
    """
    Export data to OpenTelemetry agents
    """

    def __init__(self):
        self._exporter = load_exporter()
        if self._exporter is None:
            raise ValueError("Exporter is None")

    def send_traces(self, traces):
        """Send traces to the API.

        :param traces: A list of traces.
        :return: The list of API HTTP responses.
        """
        start = time.time()
        responses = []

        #print("sending traces")

        spans = []
        # why are two loops needed?
        #print("there are {} traces".format(len(traces)))
        for trace in traces:
            #print("there are {} spans in this trace".format(len(trace)))
            for span in trace:
                #print("sending span: {}".format(trace))
                spans.append(self._ddog_to_otel_span(span))
        self._exporter.export(spans)
        return responses

    def _ddog_to_otel_span(self, ddog_span):
        # create out-of-band span (it would be better to create a SpanView)

        # context for current span
        context = trace_api.SpanContext(
            trace_id=ddog_span.trace_id, span_id=ddog_span.span_id
        )

        # parent (if one is set)
        parent = None
        if ddog_span.parent_id is not None:
            parent = trace_api.SpanContext(
                trace_id=ddog_span.trace_id, span_id=ddog_span.parent_id
            )

        # attributes
        attributes = {}
        # ddog members to opentelemetry attributes.
        # https://github.com/DataDog/dd-trace-py/blob/1f04d0fcfb3974611967004a22882b55db77433e/oteltrace/opentracer/span.py#L113
        # TODO: use constans defined in opentracer/tags.py
        if ddog_span.span_type is not None:
            # TODO(Mauricio): OpenTracing maps to 'span.type', I think
            # component is the right one for OpenTelemetry
            attributes["component"] = ddog_span.span_type

        if ddog_span.service is not None:
            attributes["service.name"] = ddog_span.service

        if ddog_span.resource is not None:
            attributes["resource.name"] = ddog_span.resource

        if ddog_span.context.sampling_priority is not None:
            attributes["sampling.priority"] = ddog_span.context.sampling_priority

        # tags
        for tag in ddog_span.meta.items():
            key = tag[0]
            value = tag[1]

            if key == "out.host":
                key = "peer.hostname"
            elif key == "out.port":
                key = "peer.port"

            attributes[key] = value

        # build span with all that info
        span = trace.Span(
            name=ddog_span.name,
            context=context,
            parent=parent,
            attributes=attributes
            # TODO: attributes, events? links?
        )

        span.start_time = ddog_span.start * 1e9
        span.end_time = (ddog_span.start + ddog_span.duration) * 1e9

        return span

