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

import pytest

from oteltrace import _worker


def test_start():
    w = _worker.PeriodicWorkerThread()
    w.start()
    assert w.is_alive()
    w.stop()
    w.join()
    assert not w.is_alive()


def test_periodic():
    results = []

    class MyWorker(_worker.PeriodicWorkerThread):
        @staticmethod
        def run_periodic():
            results.append(object())

    w = MyWorker(interval=0, daemon=False)
    w.start()
    # results should be filled really quickly, but just in case the thread is a snail, wait
    while not results:
        pass
    w.stop()
    w.join()
    assert results


def test_on_shutdown():
    results = []

    class MyWorker(_worker.PeriodicWorkerThread):
        @staticmethod
        def on_shutdown():
            results.append(object())

    w = MyWorker()
    w.start()
    assert not results
    w.stop()
    w.join()
    assert results


def test_restart():
    w = _worker.PeriodicWorkerThread()
    w.start()
    assert w.is_alive()
    w.stop()
    w.join()
    assert not w.is_alive()

    with pytest.raises(RuntimeError):
        w.start()
