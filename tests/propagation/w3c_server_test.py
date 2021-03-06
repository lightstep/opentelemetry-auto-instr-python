#!/usr/bin/env python3
#
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
"""
This server is intended to be used with the W3C tracecontext validation
Service. It implements the APIs needed to be exercised by the test bed.
"""

from oteltrace import patch_all
patch_all()

import json  # noqa: E402
import flask  # noqa: E402
import requests  # noqa: E402

from oteltrace.propagation.w3c import W3CHTTPPropagator  # noqa: E402
from oteltrace import tracer  # noqa: E402

tracer.configure(
    http_propagator=W3CHTTPPropagator,
)

app = flask.Flask(__name__)


@app.route('/verify-tracecontext', methods=['POST'])
def verify_tracecontext():
    """Upon reception of some payload, sends a request back to the designated
    url.

    This route is designed to be testable with the w3c tracecontext server /
    client test.
    """
    for action in flask.request.json:
        requests.post(
            url=action['url'],
            data=json.dumps(action['arguments']),
            headers={
                'Accept': 'application/json',
                'Content-Type': 'application/json; charset=utf-8',
            },
            timeout=5.0,
        )
    return 'hello'


if __name__ == '__main__':
    app.run(debug=True)
