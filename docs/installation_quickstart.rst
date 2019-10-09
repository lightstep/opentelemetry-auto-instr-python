.. include:: ./shared.rst


.. _Installation:

Installation + Quickstart
=========================

Before installing be sure to read through the `setup documentation`_ to ensure
your environment is ready to receive traces.


Installation
------------

Install with :code:`pip`::

$ pip install oteltrace

We strongly suggest pinning the version of the library you deploy.

Quickstart
----------

Getting started with ``oteltrace`` is as easy as prefixing your python
entry-point command with ``oteltrace-run``.

For example if you start your application with ``python app.py`` then run::

  $ oteltrace-run python app.py

For more advanced usage of ``oteltrace-run`` refer to the documentation :ref:`here<oteltracerun>`.

To find out how to trace your own code manually refer to the documentation :ref:`here<basic usage>`.


OpenTracing
-----------

``oteltrace`` also provides an OpenTracing API to the Datadog tracer so
that you can use the Datadog tracer in your OpenTracing-compatible
applications.

Installation
^^^^^^^^^^^^

Include OpenTracing with ``oteltrace``::

  $ pip install oteltrace[opentracing]

To include the OpenTracing dependency in your project with ``oteltrace``, ensure
you have the following in ``setup.py``::

    install_requires=[
        "oteltrace[opentracing]",
    ],

Configuration
^^^^^^^^^^^^^

The OpenTracing convention for initializing a tracer is to define an
initialization method that will configure and instantiate a new tracer and
overwrite the global ``opentracing.tracer`` reference.

Typically this method looks something like::

    from oteltrace.opentracer import Tracer, set_global_tracer

    def init_tracer(service_name):
        """
        Initialize a new Datadog opentracer and set it as the
        global tracer.

        This overwrites the opentracing.tracer reference.
        """
        config = {
          'agent_hostname': 'localhost',
          'agent_port': 8126,
        }
        tracer = Tracer(service_name, config=config)
        set_global_tracer(tracer)
        return tracer

For more advanced usage of OpenTracing in ``oteltrace`` refer to the
documentation :ref:`here<adv_opentracing>`.
