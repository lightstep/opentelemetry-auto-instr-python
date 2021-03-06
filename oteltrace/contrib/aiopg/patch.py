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

# 3p
import asyncio

import aiopg.connection
import psycopg2.extensions
from oteltrace.vendor import wrapt

from .connection import AIOTracedConnection
from ..psycopg.patch import _patch_extensions, \
    _unpatch_extensions, patch_conn as psycopg_patch_conn
from ...utils.wrappers import unwrap as _u


def patch():
    """ Patch monkey patches psycopg's connection function
        so that the connection's functions are traced.
    """
    if getattr(aiopg, '_opentelemetry_patch', False):
        return
    setattr(aiopg, '_opentelemetry_patch', True)

    wrapt.wrap_function_wrapper(aiopg.connection, '_connect', patched_connect)
    _patch_extensions(_aiopg_extensions)  # do this early just in case


def unpatch():
    if getattr(aiopg, '_opentelemetry_patch', False):
        setattr(aiopg, '_opentelemetry_patch', False)
        _u(aiopg.connection, '_connect')
        _unpatch_extensions(_aiopg_extensions)


@asyncio.coroutine
def patched_connect(connect_func, _, args, kwargs):
    conn = yield from connect_func(*args, **kwargs)
    return psycopg_patch_conn(conn, traced_conn_cls=AIOTracedConnection)


def _extensions_register_type(func, _, args, kwargs):
    def _unroll_args(obj, scope=None):
        return obj, scope
    obj, scope = _unroll_args(*args, **kwargs)

    # register_type performs a c-level check of the object
    # type so we must be sure to pass in the actual db connection
    if scope and isinstance(scope, wrapt.ObjectProxy):
        scope = scope.__wrapped__._conn

    return func(obj, scope) if scope else func(obj)


# extension hooks
_aiopg_extensions = [
    (psycopg2.extensions.register_type,
     psycopg2.extensions, 'register_type',
     _extensions_register_type),
]
