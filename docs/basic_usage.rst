.. _`basic usage`:

Basic Usage
===========

With ``oteltrace`` installed, the application can be instrumented.


Auto Instrumentation
--------------------

``oteltrace-run``
^^^^^^^^^^^^^^^^^

Python applications can easily be instrumented with ``oteltrace`` by using the
included ``oteltrace-run`` command. Simply prefix your Python execution command
with ``oteltrace-run`` in order to auto-instrument the libraries in your
application.

For example, if the command to run your application is::

$ python app.py

then to auto-instrument using OpenTelemetry, the corresponding command is::

$ oteltrace-run python app.py

Exporter Configuration
**********************

``oteltrace-run`` uses opentelemetry-python SDK exporters to send the traces to
different backends.
The exporter to be used is configured using the following env variables:

* ``OTEL_EXPORTER_MODULE`` specifies the python module where the exporter is implemented.
* ``OTEL_EXPORTER_FACTORY`` defines a function to be called to get an instance of the exporter.

The specific configuration for each type of exporter is defined by using the
``OTEL_EXPORTER_OPTIONS_*`` env variables.
The text after ``OTEL_EXPORTER_OPTIONS_`` will be passed to
``OTEL_EXPORTER_FACTORY`` as kwargs.

Propagator Configuration
************************

``oteltrace-run`` supports different formats to distribute the trace context.
The propagator used is defined by the ``OTEL_TRACER_PROPAGATOR`` env variable.
Currently ``w3c`` (default), ``b3`` and ``datadog`` are supported.

``patch_all``
^^^^^^^^^^^^^

TODO: how to configure exporters in this case?

To manually invoke the automatic instrumentation use ``patch_all``::

  from oteltrace import patch_all
  patch_all()

To toggle instrumentation for a particular module::

  from oteltrace import patch_all
  patch_all(redis=False, cassandra=False)

By default all supported libraries will be patched when
``patch_all`` is invoked.

**Note:** To ensure that the supported libraries are instrumented properly in
the application, they must be patched *prior* to being imported. So make sure
to call ``patch_all`` *before* importing libraries that are to be instrumented.

More information about ``patch_all`` is available in our :ref:`patch_all` API
documentation.



