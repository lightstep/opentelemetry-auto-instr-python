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

from tornado.concurrent import Future
import tornado.gen
from tornado.ioloop import IOLoop


try:
    from concurrent.futures import ThreadPoolExecutor
except ImportError:
    from tornado.concurrent import DummyExecutor

    class ThreadPoolExecutor(DummyExecutor):
        """
        Fake executor class used to test our tracer when Python 2 is used
        without the `futures` backport. This is not a real use case, but
        it's required to be defensive when we have different `Executor`
        implementations.
        """
        def __init__(self, *args, **kwargs):
            # we accept any kind of interface
            super(ThreadPoolExecutor, self).__init__()


if hasattr(tornado.gen, 'sleep'):
    sleep = tornado.gen.sleep
else:
    # Tornado <= 4.0
    def sleep(duration):
        """
        Compatibility helper that return a Future() that can be yielded.
        This is used because Tornado 4.0 doesn't have a ``gen.sleep()``
        function, that we require to test the ``TracerStackContext``.
        """
        f = Future()
        IOLoop.current().call_later(duration, lambda: f.set_result(None))
        return f
