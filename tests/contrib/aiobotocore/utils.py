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

import aiobotocore.session

from oteltrace import Pin
from contextlib import contextmanager


LOCALSTACK_ENDPOINT_URL = {
    's3': 'http://localhost:5000',
    'ec2': 'http://localhost:5001',
    'kms': 'http://localhost:5002',
    'sqs': 'http://localhost:5003',
    'lambda': 'http://localhost:5004',
    'kinesis': 'http://localhost:5005',
}


@contextmanager
def aiobotocore_client(service, tracer):
    """Helper function that creates a new aiobotocore client so that
    it is closed at the end of the context manager.
    """
    session = aiobotocore.session.get_session()
    endpoint = LOCALSTACK_ENDPOINT_URL[service]
    client = session.create_client(
        service,
        region_name='us-west-2',
        endpoint_url=endpoint,
        aws_access_key_id='aws',
        aws_secret_access_key='aws',
        aws_session_token='aws',
    )
    Pin.override(client, tracer=tracer)
    try:
        yield client
    finally:
        client.close()
