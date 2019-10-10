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


