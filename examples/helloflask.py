from ddtrace import patch_all
patch_all()

import os
import ddtrace
from flask import Flask
import requests
import opentracing
import lightstep

def set_global_tracer(tracer):
    # overwrite the opentracer reference
    opentracing.tracer = tracer

    ddtrace.tracer.configure(external_tracer=tracer)

def init_tracer(service_name):
    tracer = lightstep.Tracer(
      component_name=service_name,
      access_token=os.environ['LIGHTSTEP_ACCESS_TOKEN']
      )
    set_global_tracer(tracer)
    return tracer

init_tracer('helloflask')

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

print(ddtrace.config.flask['service_name'])

app.run(host='127.0.0.1', port=8055)

