import os

from .datadog import DatadogHTTPPropagator

_PROGPAGATOR_FACTORY = DatadogHTTPPropagator

def set_http_propagator_factory(factory):
    """Sets the propagator factory to be used globally"""
    global _PROGPAGATOR_FACTORY
    _PROGPAGATOR_FACTORY = factory

def HTTPPropagator():
    """Returns and instance of the configured propagator"""
    return _PROGPAGATOR_FACTORY()
