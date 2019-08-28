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

trace.set_preferred_tracer_implementation(lambda T: Tracer())
tracer = trace.tracer()

ddtrace.tracer.configure(otel_tracer=tracer)


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

