Web Frameworks
--------------

``oteltrace`` provides tracing support for many Python web frameworks. For each
framework ``oteltrace`` supports:

- tracing of requests [*]_: trace requests through middleware and back
- distributed tracing [*]_: trace requests across application boundaries
- automatic error tagging [*]_: spans will be marked with any errors that occur

.. [*] https://docs.datadoghq.com/tracing/
.. [*] https://docs.datadoghq.com/tracing/faq/distributed-tracing/
.. [*] "erroneous HTTP return codes" are defined as being greater than 500

.. _aiohttp:

aiohttp
^^^^^^^

.. automodule:: oteltrace.contrib.aiohttp


.. _bottle:

Bottle
^^^^^^

.. automodule:: oteltrace.contrib.bottle

.. _djangorestframework:
.. _django:

Django
^^^^^^

.. automodule:: oteltrace.contrib.django


.. _falcon:

Falcon
^^^^^^

.. automodule:: oteltrace.contrib.falcon


.. _flask:

Flask
^^^^^


.. automodule:: oteltrace.contrib.flask

.. _molten:

Molten
^^^^^^

.. automodule:: oteltrace.contrib.molten

.. _pylons:

Pylons
^^^^^^

.. automodule:: oteltrace.contrib.pylons


.. _pyramid:

Pyramid
^^^^^^^

.. automodule:: oteltrace.contrib.pyramid


.. _tornado:

Tornado
^^^^^^^

.. automodule:: oteltrace.contrib.tornado

