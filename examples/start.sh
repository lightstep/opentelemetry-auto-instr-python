#!/bin/sh

cd "$(dirname -- "${BASH_SOURCE[0]}")"
cd ..

virtualenv venv
source venv/bin/activate

# Install OTel-Python
pushd /home/mvb/kinvolk/opentelemetry/opentelemetry-python/
    # Install API
    pushd opentelemetry-api
        python setup.py install
    popd

    # Install SDK
    pushd opentelemetry-sdk
        python setup.py install
    popd
popd

pip install requests
pip install Flask

python setup.py install

python examples/helloflask.py

