from ddtrace import patch_all
patch_all()

import os
import ddtrace
from flask import Flask
import requests
import sys
import time

from opentelemetry import trace
from opentelemetry.context import Context
from opentelemetry.sdk.trace import Tracer

from opentelemetry.sdk.trace import export
from opentelemetry.sdk.trace.export.in_memory_span_exporter import (
    InMemorySpanExporter,
)

#trace.set_preferred_tracer_implementation(lambda T: Tracer())
#tracer = trace.tracer()
#
## setup in memory span exporter
#memory_exporter = InMemorySpanExporter()
#span_processor = export.SimpleExportSpanProcessor(memory_exporter)
#tracer.add_span_processor(span_processor)
#
#ddtrace.tracer.configure(otel_tracer=tracer, span_processor=span_processor)

app = Flask(__name__)

@app.route('/')
def hello_world():
    r1 = requests.get(url = "http://localhost:8055/word1")
    r2 = requests.get(url = "http://localhost:8055/word2")
    return 'Hello ' + r1.text + ' ' + r2.text

@app.route('/word1')
def hello_word1():
    r1 = requests.get(url = "http://localhost:8055/word1/details")
    return 'Alice ' + r1.text

@app.route('/word1/details')
def hello_word1_details():
    return 'Wonderland'

@app.route('/word2')
def hello_word2():
    return 'Bob'

app.run(host='127.0.0.1', port=8055)


# print captured traces to the console
#print("captured traces: ")
#memory_exporter.shutdown()
#finished_spans = memory_exporter.get_finished_spans()
#for span in finished_spans:
#    print(span.pprint())