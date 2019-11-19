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
import pymysql

# project
from oteltrace import Pin
from oteltrace.contrib.dbapi import TracedConnection
from ...ext import net, db, AppTypes

CONN_ATTR_BY_TAG = {
    net.TARGET_HOST: 'host',
    net.TARGET_PORT: 'port',
    db.USER: 'user',
    db.NAME: 'db',
}


def patch():
    wrapt.wrap_function_wrapper('pymysql', 'connect', _connect)


def unpatch():
    if isinstance(pymysql.connect, wrapt.ObjectProxy):
        pymysql.connect = pymysql.connect.__wrapped__


def _connect(func, instance, args, kwargs):
    conn = func(*args, **kwargs)
    return patch_conn(conn)


def patch_conn(conn):
    tags = {t: getattr(conn, a, '') for t, a in CONN_ATTR_BY_TAG.items()}
    pin = Pin(service='pymysql', app='pymysql', app_type=AppTypes.db, tags=tags)

    # grab the metadata from the conn
    wrapped = TracedConnection(conn, pin=pin)
    pin.onto(wrapped)
    return wrapped
