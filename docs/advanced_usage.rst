Advanced Usage
==============

Sending traces to different backends
------------------------------------

`oteltrace` can export traces to different backends by using different api implementations, it
can be controlled by passing an `api` object to :func:`oteltrace.Tracer.configure`.

The :class:`oteltrace.api_otel_exporter.APIOtel` class uses an OpenTelemetry exporters as backend.

Sending traces to different backends
------------------------------------

`oteltrace` can export traces to different backends by using different api implementations, it
can be controlled by passing an `api` object to :func:`oteltrace.Tracer.configure`.

The :class:`oteltrace.api_otel_exporter.APIOtel` class uses an OpenTelemetry exporters as backend.


Distributed Tracing
-------------------

To trace requests across hosts, the spans on the secondary hosts must be linked together by setting `trace_id`, `parent_id` and `sampling_priority`.

- On the server side, it means to read propagated attributes and set them to the active tracing context.
- On the client side, it means to propagate the attributes, commonly as a header/metadata.

`oteltrace` already provides default propagators (``w3c``, ``b3`` and ``datadog``) but you can also implement your own.

Web Frameworks
^^^^^^^^^^^^^^

Some web framework integrations support distributed tracing out of the box.

Supported web frameworks:


+-------------------+---------+
| Framework/Library | Enabled |
+===================+=========+
| :ref:`aiohttp`    | True    |
+-------------------+---------+
| :ref:`bottle`     | True    |
+-------------------+---------+
| :ref:`django`     | True    |
+-------------------+---------+
| :ref:`falcon`     | True    |
+-------------------+---------+
| :ref:`flask`      | True    |
+-------------------+---------+
| :ref:`pylons`     | True    |
+-------------------+---------+
| :ref:`pyramid`    | True    |
+-------------------+---------+
| :ref:`requests`   | True    |
+-------------------+---------+
| :ref:`tornado`    | True    |
+-------------------+---------+


HTTP Client
^^^^^^^^^^^

For distributed tracing to work, necessary tracing information must be passed
alongside a request as it flows through the system. When the request is handled
on the other side, the metadata is retrieved and the trace can continue.

To propagate the tracing information, HTTP headers are used to transmit the
required metadata to piece together the trace.

:func:`oteltrace.propagation.http.HTTPPropagator` returns an instance of the configured
propagator.

Custom
^^^^^^

You can manually propagate your tracing context over your RPC protocol. Here is
an example assuming that you have `rpc.call` function that call a `method` and
propagate a `rpc_metadata` dictionary over the wire::


    # Implement your own context propagator
    class MyRPCPropagator(object):
        def inject(self, span_context, rpc_metadata):
            rpc_metadata.update({
                'trace_id': span_context.trace_id,
                'span_id': span_context.span_id,
                'sampling_priority': span_context.sampling_priority,
            })

        def extract(self, rpc_metadata):
            return Context(
                trace_id=rpc_metadata['trace_id'],
                span_id=rpc_metadata['span_id'],
                sampling_priority=rpc_metadata['sampling_priority'],
            )

    # On the parent side
    def parent_rpc_call():
        with tracer.trace("parent_span") as span:
            rpc_metadata = {}
            propagator = MyRPCPropagator()
            propagator.inject(span.context, rpc_metadata)
            method = "<my rpc method>"
            rpc.call(method, metadata)

    # On the child side
    def child_rpc_call(method, rpc_metadata):
        propagator = MyRPCPropagator()
        context = propagator.extract(rpc_metadata)
        tracer.context_provider.activate(context)

        with tracer.trace("child_span") as span:
            span.set_meta('my_rpc_method', method)


Sampling
--------

.. _`Priority Sampling`:

Priority Sampling
^^^^^^^^^^^^^^^^^

To learn about what sampling is check out our documentation `here
<https://docs.datadoghq.com/tracing/getting_further/trace_sampling_and_storage/#priority-sampling-for-distributed-tracing>`_.

By default priorities are set on a trace by a sampler. The sampler can set the
priority to the following values:

- ``AUTO_REJECT``: the sampler automatically rejects the trace
- ``AUTO_KEEP``: the sampler automatically keeps the trace

Priority sampling is enabled by default.
When enabled, the sampler will automatically assign a priority to your traces,
depending on their service and volume.
This ensures that your sampled distributed traces will be complete.

You can also set this priority manually to either drop an uninteresting trace or
to keep an important one.
To do this, set the ``context.sampling_priority`` to one of the following:

- ``USER_REJECT``: the user asked to reject the trace
- ``USER_KEEP``: the user asked to keep the trace

When not using distributed tracing, you may change the priority at any time, as
long as the trace is not finished yet.
But it has to be done before any context propagation (fork, RPC calls) to be
effective in a distributed context.
Changing the priority after context has been propagated causes different parts
of a distributed trace to use different priorities. Some parts might be kept,
some parts might be rejected, and this can cause the trace to be partially
stored and remain incomplete.

If you change the priority, we recommend you do it as soon as possible, when the
root span has just been created::

    from oteltrace.ext.priority import USER_REJECT, USER_KEEP

    context = tracer.context_provider.active()

    # indicate to not keep the trace
    context.sampling_priority = USER_REJECT


Client Sampling
^^^^^^^^^^^^^^^

Client sampling enables the sampling of traces before they are sent to the
Agent. This can provide some performance benefit as the traces will be
dropped in the client.

The ``RateSampler`` randomly samples a percentage of traces::

    from oteltrace.sampler import RateSampler

    # Sample rate is between 0 (nothing sampled) to 1 (everything sampled).
    # Keep 20% of the traces.
    sample_rate = 0.2
    tracer.sampler = RateSampler(sample_rate)


Trace Search & Analytics
------------------------

Use `Trace Search & Analytics <https://docs.datadoghq.com/tracing/visualization/search/>`_ to filter application performance metrics and APM Events by user-defined tags. An APM event is generated every time a trace is generated.

Enabling APM events for all web frameworks can be accomplished by setting the environment variable ``OTEL_TRACE_ANALYTICS_ENABLED=true``:

* :ref:`aiohttp`
* :ref:`bottle`
* :ref:`django`
* :ref:`falcon`
* :ref:`flask`
* :ref:`molten`
* :ref:`pylons`
* :ref:`pyramid`
* :ref:`requests`
* :ref:`tornado`


For most libraries, APM events can be enabled with the environment variable ``OTEL_{INTEGRATION}_ANALYTICS_ENABLED=true``:

+----------------------+----------------------------------------+
|       Library        |          Environment Variable          |
+======================+========================================+
| :ref:`aiobotocore`   | ``OTEL_AIOBOTOCORE_ANALYTICS_ENABLED``   |
+----------------------+----------------------------------------+
| :ref:`aiopg`         | ``OTEL_AIOPG_ANALYTICS_ENABLED``         |
+----------------------+----------------------------------------+
| :ref:`boto`          | ``OTEL_BOTO_ANALYTICS_ENABLED``          |
+----------------------+----------------------------------------+
| :ref:`botocore`      | ``OTEL_BOTOCORE_ANALYTICS_ENABLED``      |
+----------------------+----------------------------------------+
| :ref:`bottle`        | ``OTEL_BOTTLE_ANALYTICS_ENABLED``        |
+----------------------+----------------------------------------+
| :ref:`cassandra`     | ``OTEL_CASSANDRA_ANALYTICS_ENABLED``     |
+----------------------+----------------------------------------+
| :ref:`elasticsearch` | ``OTEL_ELASTICSEARCH_ANALYTICS_ENABLED`` |
+----------------------+----------------------------------------+
| :ref:`falcon`        | ``OTEL_FALCON_ANALYTICS_ENABLED``        |
+----------------------+----------------------------------------+
| :ref:`flask`         | ``OTEL_FLASK_ANALYTICS_ENABLED``         |
+----------------------+----------------------------------------+
| :ref:`flask_cache`   | ``OTEL_FLASK_CACHE_ANALYTICS_ENABLED``   |
+----------------------+----------------------------------------+
| :ref:`grpc`          | ``OTEL_GRPC_ANALYTICS_ENABLED``          |
+----------------------+----------------------------------------+
| :ref:`httplib`       | ``OTEL_HTTPLIB_ANALYTICS_ENABLED``       |
+----------------------+----------------------------------------+
| :ref:`kombu`         | ``OTEL_KOMBU_ANALYTICS_ENABLED``         |
+----------------------+----------------------------------------+
| :ref:`molten`        | ``OTEL_MOLTEN_ANALYTICS_ENABLED``        |
+----------------------+----------------------------------------+
| :ref:`pylibmc`       | ``OTEL_PYLIBMC_ANALYTICS_ENABLED``       |
+----------------------+----------------------------------------+
| :ref:`pylons`        | ``OTEL_PYLONS_ANALYTICS_ENABLED``        |
+----------------------+----------------------------------------+
| :ref:`pymemcache`    | ``OTEL_PYMEMCACHE_ANALYTICS_ENABLED``    |
+----------------------+----------------------------------------+
| :ref:`pymongo`       | ``OTEL_PYMONGO_ANALYTICS_ENABLED``       |
+----------------------+----------------------------------------+
| :ref:`redis`         | ``OTEL_REDIS_ANALYTICS_ENABLED``         |
+----------------------+----------------------------------------+
| :ref:`rediscluster`  | ``OTEL_REDISCLUSTER_ANALYTICS_ENABLED``  |
+----------------------+----------------------------------------+
| :ref:`sqlalchemy`    | ``OTEL_SQLALCHEMY_ANALYTICS_ENABLED``    |
+----------------------+----------------------------------------+
| :ref:`vertica`       | ``OTEL_VERTICA_ANALYTICS_ENABLED``       |
+----------------------+----------------------------------------+

For datastore libraries that extend another, use the setting for the underlying library:

+------------------------+----------------------------------+
|        Library         |       Environment Variable       |
+========================+==================================+
| :ref:`mongoengine`     | ``OTEL_PYMONGO_ANALYTICS_ENABLED`` |
+------------------------+----------------------------------+
| :ref:`mysql-connector` | ``OTEL_DBAPI2_ANALYTICS_ENABLED``  |
+------------------------+----------------------------------+
| :ref:`mysqldb`         | ``OTEL_DBAPI2_ANALYTICS_ENABLED``  |
+------------------------+----------------------------------+
| :ref:`psycopg2`        | ``OTEL_DBAPI2_ANALYTICS_ENABLED``  |
+------------------------+----------------------------------+
| :ref:`pymysql`         | ``OTEL_DBAPI2_ANALYTICS_ENABLED``  |
+------------------------+----------------------------------+
| :ref:`sqllite`         | ``OTEL_DBAPI2_ANALYTICS_ENABLED``  |
+------------------------+----------------------------------+

Where environment variables are not used for configuring the tracer, the instructions for configuring trace analytics is provided in the library documentation:

* :ref:`aiohttp`
* :ref:`django`
* :ref:`pyramid`
* :ref:`requests`
* :ref:`tornado`

Resolving deprecation warnings
------------------------------
Before upgrading, it’s a good idea to resolve any deprecation warnings raised by your project.
These warnings must be fixed before upgrading, otherwise the ``oteltrace`` library
will not work as expected. Our deprecation messages include the version where
the behavior is altered or removed.

In Python, deprecation warnings are silenced by default. To enable them you may
add the following flag or environment variable::

    $ python -Wall app.py

    # or

    $ PYTHONWARNINGS=all python app.py


Trace Filtering
---------------

It is possible to filter or modify traces before they are sent to the Agent by
configuring the tracer with a filters list. For instance, to filter out
all traces of incoming requests to a specific url::

    Tracer.configure(settings={
        'FILTERS': [
            FilterRequestsOnUrl(r'http://test\.example\.com'),
        ],
    })

All the filters in the filters list will be evaluated sequentially
for each trace and the resulting trace will either be sent to the Agent or
discarded depending on the output.

**Use the standard filters**

The library comes with a ``FilterRequestsOnUrl`` filter that can be used to
filter out incoming requests to specific urls:

.. autoclass:: oteltrace.filters.FilterRequestsOnUrl
    :members:

**Write a custom filter**

Creating your own filters is as simple as implementing a class with a
``process_trace`` method and adding it to the filters parameter of
Tracer.configure. process_trace should either return a trace to be fed to the
next step of the pipeline or ``None`` if the trace should be discarded::

    class FilterExample(object):
        def process_trace(self, trace):
            # write here your logic to return the `trace` or None;
            # `trace` instance is owned by the thread and you can alter
            # each single span or the whole trace if needed

    # And then instantiate it with
    filters = [FilterExample()]
    Tracer.configure(settings={'FILTERS': filters})

(see filters.py for other example implementations)

.. _`Logs Injection`:

Logs Injection
--------------

.. automodule:: oteltrace.contrib.logging

HTTP layer
----------

Query String Tracing
^^^^^^^^^^^^^^^^^^^^

It is possible to store the query string of the URL — the part after the ``?``
in your URL — in the ``url.query.string`` tag.

Configuration can be provided both at the global level and at the integration level.

Examples::

    from oteltrace import config

    # Global config
    config.http.trace_query_string = True

    # Integration level config, e.g. 'falcon'
    config.falcon.http.trace_query_string = True

..  _http-headers-tracing:

Headers tracing
^^^^^^^^^^^^^^^


For a selected set of integrations, it is possible to store http headers from both requests and responses in tags.

Configuration can be provided both at the global level and at the integration level.

Examples::

    from oteltrace import config

    # Global config
    config.trace_headers([
        'user-agent',
        'transfer-encoding',
    ])

    # Integration level config, e.g. 'falcon'
    config.falcon.http.trace_headers([
        'user-agent',
        'some-other-header',
    ])

The following rules apply:
  - headers configuration is based on a whitelist. If a header does not appear in the whitelist, it won't be traced.
  - headers configuration is case-insensitive.
  - if you configure a specific integration, e.g. 'requests', then such configuration overrides the default global
    configuration, only for the specific integration.
  - if you do not configure a specific integration, then the default global configuration applies, if any.
  - if no configuration is provided (neither global nor integration-specific), then headers are not traced.

Once you configure your application for tracing, you will have the headers attached to the trace as tags, with a
structure like in the following example::

    http {
      method  GET
      request {
        headers {
          user_agent  my-app/0.0.1
        }
      }
      response {
        headers {
          transfer_encoding  chunked
        }
      }
      status_code  200
      url  https://api.github.com/events
    }


.. _oteltracerun:

``oteltrace-run``
---------------

``oteltrace-run`` will trace :ref:`supported<Supported Libraries>` web frameworks
and database modules without the need for changing your code::

  $ oteltrace-run -h

  Execute the given Python program, after configuring it
  to emit OpenTelemetry traces.

  Append command line arguments to your program as usual.

  Usage: [ENV_VARS] oteltrace-run <my_program>


The available environment variables for ``oteltrace-run`` are:

* ``OPENTELEMETRY_TRACE_ENABLED=true|false`` (default: true): Enable web framework and
  library instrumentation. When false, your application code will not generate
  any traces.
* ``OPENTELEMETRY_ENV`` (no default): Set an application's environment e.g. ``prod``,
  ``pre-prod``, ``stage``
* ``OPENTELEMETRY_TRACE_DEBUG=true|false`` (default: false): Enable debug logging in
  the tracer
* ``OPENTELEMETRY_SERVICE_NAME`` (no default): override the service name to be used
  for this program. This value is passed through when setting up middleware for
  web framework integrations (e.g. pylons, flask, django). For tracing without a
  web integration, prefer setting the service name in code.
* ``OPENTELEMETRY_PATCH_MODULES=module:patch,module:patch...`` e.g.
  ``boto:true,redis:false``: override the modules patched for this execution of
  the program (default: none)
* ``OPENTELEMETRY_TRACE_AGENT_HOSTNAME=localhost``: override the address of the trace
  agent host that the default tracer will attempt to submit to  (default:
  ``localhost``)
* ``OPENTELEMETRY_TRACE_AGENT_PORT=8126``: override the port that the default tracer
  will submit to  (default: 8126)
* ``OPENTELEMETRY_PRIORITY_SAMPLING`` (default: true): enables :ref:`Priority
  Sampling`
* ``OTEL_LOGS_INJECTION`` (default: false): enables :ref:`Logs Injection`

Exporter Configuration
^^^^^^^^^^^^^^^^^^^^^^

``oteltrace-run`` uses OpenTelemetry SDK exporters to send the traces to
different backends.
The exporter to be used is configured using the following env variables:

* ``OTEL_EXPORTER_MODULE`` specifies the python module where the exporter is implemented.
* ``OTEL_EXPORTER_FACTORY`` defines a function to be called to get an instance of the exporter.

The specific configuration for each type of exporter is defined by using the
``OTEL_EXPORTER_OPTIONS_*`` env variables.
The text after ``OTEL_EXPORTER_OPTIONS_`` will be passed to
``OTEL_EXPORTER_FACTORY`` as kwargs.

Propagator Configuration
^^^^^^^^^^^^^^^^^^^^^^^^

``oteltrace-run`` supports different formats to distribute the trace context.
The propagator used is defined by the ``OTEL_TRACER_PROPAGATOR`` env variable.
Currently ``w3c`` (default), ``b3`` and ``datadog`` are supported.

``oteltrace-run`` respects a variety of common entrypoints for web applications:

- ``oteltrace-run python my_app.py``
- ``oteltrace-run python manage.py runserver``
- ``oteltrace-run gunicorn myapp.wsgi:application``
- ``oteltrace-run uwsgi --http :9090 --wsgi-file my_app.py``


Pass along command-line arguments as your program would normally expect them::

$ oteltrace-run gunicorn myapp.wsgi:application --max-requests 1000 --statsd-host localhost:8125

If you're running in a Kubernetes cluster and still don't see your traces, make
sure your application has a route to the tracing Agent. An easy way to test
this is with a::

$ pip install ipython
$ OPENTELEMETRY_TRACE_DEBUG=true oteltrace-run ipython

Because iPython uses SQLite, it will be automatically instrumented and your
traces should be sent off. If an error occurs, a message will be displayed in
the console, and changes can be made as needed.


API
---

``Tracer``
^^^^^^^^^^
.. autoclass:: oteltrace.Tracer
    :members:
    :special-members: __init__


``Span``
^^^^^^^^
.. autoclass:: oteltrace.Span
    :members:
    :special-members: __init__

``Pin``
^^^^^^^
.. autoclass:: oteltrace.Pin
    :members:
    :special-members: __init__

``APIOtel``
^^^^^^^^^^^
.. autoclass:: oteltrace.api_otel_exporter.APIOtel
    :members:
    :special-members: __init__

.. _patch_all:

``patch_all``
^^^^^^^^^^^^^

.. autofunction:: oteltrace.monkey.patch_all

``patch``
^^^^^^^^^
.. autofunction:: oteltrace.monkey.patch

.. toctree::
   :maxdepth: 2
