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
from oteltrace.vendor import wrapt
import mysql.connector

# project
from oteltrace import Pin
from oteltrace.contrib.dbapi import TracedConnection
from ...ext import net, db, AppTypes


CONN_ATTR_BY_TAG = {
    net.TARGET_HOST: 'server_host',
    net.TARGET_PORT: 'server_port',
    db.USER: 'user',
    db.NAME: 'database',
}


def patch():
    wrapt.wrap_function_wrapper('mysql.connector', 'connect', _connect)
    # `Connect` is an alias for `connect`, patch it too
    if hasattr(mysql.connector, 'Connect'):
        mysql.connector.Connect = mysql.connector.connect


def unpatch():
    if isinstance(mysql.connector.connect, wrapt.ObjectProxy):
        mysql.connector.connect = mysql.connector.connect.__wrapped__
        if hasattr(mysql.connector, 'Connect'):
            mysql.connector.Connect = mysql.connector.connect


def _connect(func, instance, args, kwargs):
    conn = func(*args, **kwargs)
    return patch_conn(conn)


def patch_conn(conn):

    tags = {t: getattr(conn, a) for t, a in CONN_ATTR_BY_TAG.items() if getattr(conn, a, '') != ''}
    pin = Pin(service='mysql', app='mysql', app_type=AppTypes.db, tags=tags)

    # grab the metadata from the conn
    wrapped = TracedConnection(conn, pin=pin)
    pin.onto(wrapped)
    return wrapped
