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

import time
from unittest import TestCase

import pytest

import mock

from oteltrace.span import Span
from oteltrace.internal.writer import AgentWriter, Q, Empty


class RemoveAllFilter():
    def __init__(self):
        self.filtered_traces = 0

    def process_trace(self, trace):
        self.filtered_traces += 1
        return None


class KeepAllFilter():
    def __init__(self):
        self.filtered_traces = 0

    def process_trace(self, trace):
        self.filtered_traces += 1
        return trace


class AddTagFilter():
    def __init__(self, tag_name):
        self.tag_name = tag_name
        self.filtered_traces = 0

    def process_trace(self, trace):
        self.filtered_traces += 1
        for span in trace:
            span.set_tag(self.tag_name, 'A value')
        return trace


class DummyAPI(object):
    def __init__(self):
        self.traces = []

    def send_traces(self, traces):
        responses = []
        for trace in traces:
            self.traces.append(trace)
            response = mock.Mock()
            response.status = 200
            responses.append(response)
        return responses


class FailingAPI(object):

    @staticmethod
    def send_traces(traces):
        return [Exception('oops')]


class AgentWriterTests(TestCase):
    N_TRACES = 11

    def create_worker(self, filters=None, api_class=DummyAPI, enable_stats=False):
        self.metrics_client = mock.Mock()
        worker = AgentWriter(metrics_client=self.metrics_client, filters=filters)
        worker._ENABLE_STATS = enable_stats
        worker._STATS_EVERY_INTERVAL = 1
        self.api = api_class()
        worker.api = self.api
        for i in range(self.N_TRACES):
            worker.write([
                Span(tracer=None, name='name', trace_id=i, span_id=j, parent_id=j - 1 or None)
                for j in range(7)
            ])
        worker.stop()
        worker.join()
        return worker

    def test_filters_keep_all(self):
        filtr = KeepAllFilter()
        self.create_worker([filtr])
        self.assertEqual(len(self.api.traces), self.N_TRACES)
        self.assertEqual(filtr.filtered_traces, self.N_TRACES)

    def test_filters_remove_all(self):
        filtr = RemoveAllFilter()
        self.create_worker([filtr])
        self.assertEqual(len(self.api.traces), 0)
        self.assertEqual(filtr.filtered_traces, self.N_TRACES)

    def test_filters_add_tag(self):
        tag_name = 'Tag'
        filtr = AddTagFilter(tag_name)
        self.create_worker([filtr])
        self.assertEqual(len(self.api.traces), self.N_TRACES)
        self.assertEqual(filtr.filtered_traces, self.N_TRACES)
        for trace in self.api.traces:
            for span in trace:
                self.assertIsNotNone(span.get_tag(tag_name))

    def test_filters_short_circuit(self):
        filtr = KeepAllFilter()
        filters = [RemoveAllFilter(), filtr]
        self.create_worker(filters)
        self.assertEqual(len(self.api.traces), 0)
        self.assertEqual(filtr.filtered_traces, 0)

    def test_no_dogstats(self):
        worker = self.create_worker()
        assert worker._ENABLE_STATS is False
        assert [
        ] == self.metrics_client.gauge.mock_calls

    def test_metrics_client(self):
        self.create_worker(enable_stats=True)
        assert [
            mock.call('opentelemetry.tracer.queue.max_length', 1000),
            mock.call('opentelemetry.tracer.queue.length', 11),
            mock.call('opentelemetry.tracer.queue.size', mock.ANY),
            mock.call('opentelemetry.tracer.queue.spans', 77),
        ] == self.metrics_client.gauge.mock_calls
        increment_calls = [
            mock.call('opentelemetry.tracer.queue.dropped', 0),
            mock.call('opentelemetry.tracer.queue.accepted', 11),
            mock.call('opentelemetry.tracer.queue.accepted_lengths', 77),
            mock.call('opentelemetry.tracer.queue.accepted_size', mock.ANY),
            mock.call('opentelemetry.tracer.traces.filtered', 0),
            mock.call('opentelemetry.tracer.api.requests', 11),
            mock.call('opentelemetry.tracer.api.errors', 0),
            mock.call('opentelemetry.tracer.api.responses', 11, tags=['status:200']),
        ]
        if hasattr(time, 'thread_time_ns'):
            increment_calls.append(mock.call('opentelemetry.tracer.writer.cpu_time', mock.ANY))
        assert increment_calls == self.metrics_client.increment.mock_calls

    def test_metrics_client_failing_api(self):
        self.create_worker(api_class=FailingAPI, enable_stats=True)
        assert [
            mock.call('opentelemetry.tracer.queue.max_length', 1000),
            mock.call('opentelemetry.tracer.queue.length', 11),
            mock.call('opentelemetry.tracer.queue.size', mock.ANY),
            mock.call('opentelemetry.tracer.queue.spans', 77),
        ] == self.metrics_client.gauge.mock_calls
        increment_calls = [
            mock.call('opentelemetry.tracer.queue.dropped', 0),
            mock.call('opentelemetry.tracer.queue.accepted', 11),
            mock.call('opentelemetry.tracer.queue.accepted_lengths', 77),
            mock.call('opentelemetry.tracer.queue.accepted_size', mock.ANY),
            mock.call('opentelemetry.tracer.traces.filtered', 0),
            mock.call('opentelemetry.tracer.api.requests', 1),
            mock.call('opentelemetry.tracer.api.errors', 1),
        ]
        if hasattr(time, 'thread_time_ns'):
            increment_calls.append(mock.call('opentelemetry.tracer.writer.cpu_time', mock.ANY))
        assert increment_calls == self.metrics_client.increment.mock_calls


def test_queue_full():
    q = Q(maxsize=3)
    q.put([1])
    q.put(2)
    q.put([3])
    q.put([4, 4])
    assert (list(q.queue) == [[1], 2, [4, 4]] or
            list(q.queue) == [[1], [4, 4], [3]] or
            list(q.queue) == [[4, 4], 2, [3]])
    assert q.dropped == 1
    assert q.accepted == 4
    assert q.accepted_lengths == 5
    assert q.accepted_size >= 100
    dropped, accepted, accepted_lengths, accepted_size = q.reset_stats()
    assert dropped == 1
    assert accepted == 4
    assert accepted_lengths == 5
    assert accepted_size >= 100


def test_queue_get():
    q = Q(maxsize=3)
    q.put(1)
    q.put(2)
    assert list(q.get()) == [1, 2]
    with pytest.raises(Empty):
        q.get(block=False)
