Example 2: Using ``patch_all``
==============================

This example shows how to configure the OpenTelemetry Jaeger and the HTTP
propagator using the oteltrace API.

Please be sure that you have installed the Jaeger OpenTelemetry exporter and
that the Jaeger Agent is running as stated in `example1 <../example1/Readme.rst>`_


Configuring the exporter
------------------------

In order to use an OpenTelemetry exporter it has to be created and then
provide it in an APIOtel object to ``tracer.configure()``.
The following code snippet is an example of how it can be done with Jaeger:

::

   import oteltrace

   from oteltrace.api_otel_exporter import APIOtel
   from opentelemetry.ext.jaeger import JaegerSpanExporter


   # create Jaeger Exporter
   jaeger_exporter = JaegerSpanExporter(
       service_name='example2',
   )

   oteltrace.tracer.configure(
       api=APIOtel(exporter=jaeger_exporter),
   )

::

   # parameters to be passed to the factory function
   export OTEL_EXPORTER_OPTIONS_service_name="example2"

Optional: Choosing the HTTP trace context propagator
----------------------------------------------------

``oteltrace`` allows to specify the HTTP propagator to be used by the
different integrations.
``w3c``, ``b3`` and ``DataDog`` propagators are shipped with ``oteltrace``,
but also custom implementation could be passed to ``tracer.configure()``.

The following code snippet shows how to set ``w3c`` as the HTTP propagator.

::

   import oteltrace

   from oteltrace.propagation.w3c import W3CHTTPPropagator

   oteltrace.tracer.configure(
       http_propagator=W3CHTTPPropagator,
   )

Running the example
-------------------

Finally, ``oteltrace-run`` can be executed.

::

   python examples/example2/example2.py

Perform a request to the example service:

::

   curl http://127.0.0.1:8055/

Now you can open the Jaeger UI in your browser http://localhost:16686/ to see the traces.
