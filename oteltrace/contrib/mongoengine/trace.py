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

# project
import oteltrace
from oteltrace.ext import mongo as mongox
from oteltrace.contrib.pymongo.client import TracedMongoClient


# TODO(Benjamin): we should instrument register_connection instead, because more generic
# We should also extract the "alias" attribute and set it as a meta
class WrappedConnect(wrapt.ObjectProxy):
    """ WrappedConnect wraps mongoengines 'connect' function to ensure
        that all returned connections are wrapped for tracing.
    """

    def __init__(self, connect):
        super(WrappedConnect, self).__init__(connect)
        oteltrace.Pin(service=mongox.TYPE, tracer=oteltrace.tracer).onto(self)

    def __call__(self, *args, **kwargs):
        client = self.__wrapped__(*args, **kwargs)
        pin = oteltrace.Pin.get_from(self)
        if pin:
            # mongoengine uses pymongo internally, so we can just piggyback on the
            # existing pymongo integration and make sure that the connections it
            # uses internally are traced.
            client = TracedMongoClient(client)
            oteltrace.Pin(service=pin.service, tracer=pin.tracer).onto(client)

        return client
