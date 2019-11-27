# Copyright 2019, OpenTelemetry Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import gevent
import gevent.pool
import oteltrace

from .greenlet import TracedGreenlet, TracedIMap, TracedIMapUnordered, GEVENT_VERSION
from .provider import GeventContextProvider
from ...provider import DefaultContextProvider


__Greenlet = gevent.Greenlet
__IMap = gevent.pool.IMap
__IMapUnordered = gevent.pool.IMapUnordered


def patch():
    """
    Patch the gevent module so that all references to the
    internal ``Greenlet`` class points to the ``OpenTelemetryGreenlet``
    class.

    This action ensures that if a user extends the ``Greenlet``
    class, the ``TracedGreenlet`` is used as a parent class.
    """
    _replace(TracedGreenlet, TracedIMap, TracedIMapUnordered)
    oteltrace.tracer.configure(context_provider=GeventContextProvider())


def unpatch():
    """
    Restore the original ``Greenlet``. This function must be invoked
    before executing application code, otherwise the ``OpenTelemetryGreenlet``
    class may be used during initialization.
    """
    _replace(__Greenlet, __IMap, __IMapUnordered)
    oteltrace.tracer.configure(context_provider=DefaultContextProvider())


def _replace(g_class, imap_class, imap_unordered_class):
    """
    Utility function that replace the gevent Greenlet class with the given one.
    """
    # replace the original Greenlet classes with the new one
    gevent.greenlet.Greenlet = g_class

    if GEVENT_VERSION >= (1, 3):
        # For gevent >= 1.3.0, IMap and IMapUnordered were pulled out of
        # gevent.pool and into gevent._imap
        gevent._imap.IMap = imap_class
        gevent._imap.IMapUnordered = imap_unordered_class
        gevent.pool.IMap = gevent._imap.IMap
        gevent.pool.IMapUnordered = gevent._imap.IMapUnordered
        gevent.pool.Greenlet = gevent.greenlet.Greenlet
    else:
        # For gevent < 1.3, only patching of gevent.pool classes necessary
        gevent.pool.IMap = imap_class
        gevent.pool.IMapUnordered = imap_unordered_class

    gevent.pool.Group.greenlet_class = g_class

    # replace gevent shortcuts
    gevent.Greenlet = gevent.greenlet.Greenlet
    gevent.spawn = gevent.greenlet.Greenlet.spawn
    gevent.spawn_later = gevent.greenlet.Greenlet.spawn_later
