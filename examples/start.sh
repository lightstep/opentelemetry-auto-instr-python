#!/bin/sh

cd "$(dirname -- "${BASH_SOURCE[0]}")"
cd ..

virtualenv venv
source venv/bin/activate

pip install requests
pip install lightstep
pip install Flask
pip install lightstep opentracing

python setup.py install

python examples/helloflask.py
