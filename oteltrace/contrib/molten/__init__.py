"""
The molten web framework is automatically traced by ``oteltrace`` when calling ``patch``::

    from molten import App, Route
    from oteltrace import patch_all; patch_all(molten=True)

    def hello(name: str, age: int) -> str:
        return f'Hello {age} year old named {name}!'
    app = App(routes=[Route('/hello/{name}/{age}', hello)])


You may also enable molten tracing automatically via ``oteltrace-run``::

    oteltrace-run python app.py


Configuration
~~~~~~~~~~~~~

.. py:data:: oteltrace.config.molten['distributed_tracing']

   Whether to parse distributed tracing headers from requests received by your Molten app.

   Default: ``True``

.. py:data:: oteltrace.config.molten['analytics_enabled']

   Whether to generate APM events in Trace Search & Analytics.

   Can also be enabled with the ``OTEL_MOLTEN_ANALYTICS_ENABLED`` environment variable.

   Default: ``None``

.. py:data:: oteltrace.config.molten['service_name']

   The service name reported for your Molten app.

   Can also be configured via the ``OTEL_MOLTEN_SERVICE_NAME`` environment variable.

   Default: ``'molten'``
"""
from ...utils.importlib import require_modules

required_modules = ['molten']

with require_modules(required_modules) as missing_modules:
    if not missing_modules:
        from . import patch as _patch

        patch = _patch.patch
        unpatch = _patch.unpatch

        __all__ = ['patch', 'unpatch']
