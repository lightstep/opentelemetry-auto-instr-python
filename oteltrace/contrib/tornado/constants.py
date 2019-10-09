"""
This module defines Tornado settings that are shared between
integration modules.
"""
CONFIG_KEY = 'opentelemetry_trace'
REQUEST_CONTEXT_KEY = 'opentelemetry_context'
REQUEST_SPAN_KEY = '__opentelemetry_request_span'
FUTURE_SPAN_KEY = '__opentelemetry_future_span'
PARENT_SPAN_KEY = '__opentelemetry_parent_span'
