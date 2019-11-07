Example 1: Using the OpenTelemetry Jaeger Exporter with ``oteltrace-run``
==========================================================================

This example shows how to configure the OpenTelemetry Jaeger exporter with
``oteltrace-run``.

.. _jaeger_exporter_install:

Installation
------------

This example requires ``oteltrace-py``, ``opentelemetry-api``, ``opentelemetry-sdk`` and the Jaeger exporter.

We recommend to use virtualenv to create a new environment to run these examples.

::

   # create the virtual environment
   virtualenv oteltracepy
   # activate it
   source oteltracepy/bin/activate

Installing oteltrace-py and dependencies
****************************************

::

   # install oteltrace-py (will install opentelemetry as well)
   cd oteltrace-py
   pip install -e .

   # install dependencies for the examples
   pip install Flask requests

Installing the OpenTelemetry Jaeger exporter
********************************************

The OpenTelemetry Jaeger exporter doesn't have a PyPI package yet, follow
these instructions to install it from source:

::

   git clone https://github.com/open-telemetry/opentelemetry-python
   cd opentelemetry-python
   pip install -e ./ext/opentelemetry-ext-jaeger

.. _run_jaeger_agent:

Running the Jaeger agent
------------------------

The easiest way to run the Jaeger agent is by using the ``all-in-one`` docker image.
For more details please visit `<https://www.jaegertracing.io/docs/1.13/getting-started/>`_.

::

   docker run --rm  \
     -p 6831:6831/udp \
     -p 6832:6832/udp \
     -p 16686:16686 \
     jaegertracing/all-in-one:1.13

Configuring the exporter
------------------------

In order to use an OpenTelemetry SDK exporter with ``oteltrace-run`` a series
of env variables has to be set before executing.

The ``OTEL_EXPORTER_MODULE`` variable defines a python module where the
exporter is implemented and ``OTEL_EXPORTER_FACTORY`` is a function to be
called inside that module to get an instance of the exporter.
When ``oteltrace-run`` is executed it loads ``OTEL_EXPORTER_MODULE`` and then
calls ``OTEL_EXPORTER_FACTORY`` to get an instance of the exporter.

::

   # module where the opentelemetry SDK exporter is implemented
   export OTEL_EXPORTER_MODULE=opentelemetry.ext.jaeger
   # factory function that returns an instance of the exporter (constructor in this case)
   export OTEL_EXPORTER_FACTORY=JaegerSpanExporter


Specific configuration options for the exporter can be set by using the
``OTEL_EXPORTER_OPTIONS_`` env variables.
The list of different variables defined by the user is passed to the factory
function.

For this example it's only needed to configure the ``service_name`` parameter
as other default values will work out of the box.

::

   # parameters to be passed to the factory function
   export OTEL_EXPORTER_OPTIONS_service_name="example1"

Optional: Choosing the HTTP trace context propagator
----------------------------------------------------

``oteltrace`` implements the ``b3``, ``w3c`` and ``DataDog`` HTTP trace
context propagators.

The ``OTEL_TRACER_PROPAGATOR`` env variable determines the propagator to be
used.

::

   # use w3c trace propagator
   export OTEL_TRACER_PROPAGATOR=w3c


Running the example
-------------------

Finally, ``oteltrace-run`` can be executed.

::

   oteltrace-run python examples/example1/example1.py

Using another terminal, perform a request to the example service:

::

   curl http://127.0.0.1:8055/

Now you can open the Jaeger UI in your browser http://localhost:16686/ to see the traces.
