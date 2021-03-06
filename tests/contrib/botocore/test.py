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

# 3p
import botocore.session
from moto import mock_s3, mock_ec2, mock_lambda, mock_sqs, mock_kinesis, mock_kms

# project
from oteltrace import Pin
from oteltrace.constants import ANALYTICS_SAMPLE_RATE_KEY
from oteltrace.contrib.botocore.patch import patch, unpatch
from oteltrace.ext import http
from oteltrace.compat import stringify

# testing
from ...base import BaseTracerTestCase


class BotocoreTest(BaseTracerTestCase):
    """Botocore integration testsuite"""

    TEST_SERVICE = 'test-botocore-tracing'

    def setUp(self):
        patch()

        self.session = botocore.session.get_session()
        self.session.set_credentials(access_key='access-key', secret_key='secret-key')

        super(BotocoreTest, self).setUp()

    def tearDown(self):
        super(BotocoreTest, self).tearDown()

        unpatch()

    @mock_ec2
    def test_traced_client(self):
        ec2 = self.session.create_client('ec2', region_name='us-west-2')
        Pin(service=self.TEST_SERVICE, tracer=self.tracer).onto(ec2)

        ec2.describe_instances()

        spans = self.get_spans()
        assert spans
        span = spans[0]
        self.assertEqual(len(spans), 1)
        self.assertEqual(span.get_tag('aws.agent'), 'botocore')
        self.assertEqual(span.get_tag('aws.region'), 'us-west-2')
        self.assertEqual(span.get_tag('aws.operation'), 'DescribeInstances')
        self.assertEqual(span.get_tag(http.STATUS_CODE), '200')
        self.assertEqual(span.get_tag('retry_attempts'), '0')
        self.assertEqual(span.service, 'test-botocore-tracing.ec2')
        self.assertEqual(span.resource, 'ec2.describeinstances')
        self.assertEqual(span.name, 'ec2.command')
        self.assertEqual(span.span_type, 'http')
        self.assertIsNone(span.get_metric(ANALYTICS_SAMPLE_RATE_KEY))

    @mock_ec2
    def test_traced_client_analytics(self):
        with self.override_config(
                'botocore',
                dict(analytics_enabled=True, analytics_sample_rate=0.5)
        ):
            ec2 = self.session.create_client('ec2', region_name='us-west-2')
            Pin(service=self.TEST_SERVICE, tracer=self.tracer).onto(ec2)
            ec2.describe_instances()

        spans = self.get_spans()
        assert spans
        span = spans[0]
        self.assertEqual(span.get_metric(ANALYTICS_SAMPLE_RATE_KEY), 0.5)

    @mock_s3
    def test_s3_client(self):
        s3 = self.session.create_client('s3', region_name='us-west-2')
        Pin(service=self.TEST_SERVICE, tracer=self.tracer).onto(s3)

        s3.list_buckets()
        s3.list_buckets()

        spans = self.get_spans()
        assert spans
        span = spans[0]
        self.assertEqual(len(spans), 2)
        self.assertEqual(span.get_tag('aws.operation'), 'ListBuckets')
        self.assertEqual(span.get_tag(http.STATUS_CODE), '200')
        self.assertEqual(span.service, 'test-botocore-tracing.s3')
        self.assertEqual(span.resource, 's3.listbuckets')

        # testing for span error
        self.reset()
        try:
            s3.list_objects(bucket='mybucket')
        except Exception:
            spans = self.get_spans()
            assert spans
            span = spans[0]
            self.assertEqual(span.error, 1)
            self.assertEqual(span.resource, 's3.listobjects')

    @mock_s3
    def test_s3_put(self):
        params = dict(Key='foo', Bucket='mybucket', Body=b'bar')
        s3 = self.session.create_client('s3', region_name='us-west-2')
        Pin(service=self.TEST_SERVICE, tracer=self.tracer).onto(s3)
        s3.create_bucket(Bucket='mybucket')
        s3.put_object(**params)

        spans = self.get_spans()
        assert spans
        span = spans[0]
        self.assertEqual(len(spans), 2)
        self.assertEqual(span.get_tag('aws.operation'), 'CreateBucket')
        self.assertEqual(span.get_tag(http.STATUS_CODE), '200')
        self.assertEqual(span.service, 'test-botocore-tracing.s3')
        self.assertEqual(span.resource, 's3.createbucket')
        self.assertEqual(spans[1].get_tag('aws.operation'), 'PutObject')
        self.assertEqual(spans[1].resource, 's3.putobject')
        self.assertEqual(spans[1].get_tag('params.Key'), stringify(params['Key']))
        self.assertEqual(spans[1].get_tag('params.Bucket'), stringify(params['Bucket']))
        # confirm blacklisted
        self.assertIsNone(spans[1].get_tag('params.Body'))

    @mock_sqs
    def test_sqs_client(self):
        sqs = self.session.create_client('sqs', region_name='us-east-1')
        Pin(service=self.TEST_SERVICE, tracer=self.tracer).onto(sqs)

        sqs.list_queues()

        spans = self.get_spans()
        assert spans
        span = spans[0]
        self.assertEqual(len(spans), 1)
        self.assertEqual(span.get_tag('aws.region'), 'us-east-1')
        self.assertEqual(span.get_tag('aws.operation'), 'ListQueues')
        self.assertEqual(span.get_tag(http.STATUS_CODE), '200')
        self.assertEqual(span.service, 'test-botocore-tracing.sqs')
        self.assertEqual(span.resource, 'sqs.listqueues')

    @mock_kinesis
    def test_kinesis_client(self):
        kinesis = self.session.create_client('kinesis', region_name='us-east-1')
        Pin(service=self.TEST_SERVICE, tracer=self.tracer).onto(kinesis)

        kinesis.list_streams()

        spans = self.get_spans()
        assert spans
        span = spans[0]
        self.assertEqual(len(spans), 1)
        self.assertEqual(span.get_tag('aws.region'), 'us-east-1')
        self.assertEqual(span.get_tag('aws.operation'), 'ListStreams')
        self.assertEqual(span.get_tag(http.STATUS_CODE), '200')
        self.assertEqual(span.service, 'test-botocore-tracing.kinesis')
        self.assertEqual(span.resource, 'kinesis.liststreams')

    @mock_kinesis
    def test_unpatch(self):
        kinesis = self.session.create_client('kinesis', region_name='us-east-1')
        Pin(service=self.TEST_SERVICE, tracer=self.tracer).onto(kinesis)

        unpatch()

        kinesis.list_streams()
        spans = self.get_spans()
        assert not spans, spans

    @mock_sqs
    def test_double_patch(self):
        sqs = self.session.create_client('sqs', region_name='us-east-1')
        Pin(service=self.TEST_SERVICE, tracer=self.tracer).onto(sqs)

        patch()
        patch()

        sqs.list_queues()

        spans = self.get_spans()
        assert spans
        self.assertEqual(len(spans), 1)

    @mock_lambda
    def test_lambda_client(self):
        lamb = self.session.create_client('lambda', region_name='us-east-1')
        Pin(service=self.TEST_SERVICE, tracer=self.tracer).onto(lamb)

        lamb.list_functions()

        spans = self.get_spans()
        assert spans
        span = spans[0]
        self.assertEqual(len(spans), 1)
        self.assertEqual(span.get_tag('aws.region'), 'us-east-1')
        self.assertEqual(span.get_tag('aws.operation'), 'ListFunctions')
        self.assertEqual(span.get_tag(http.STATUS_CODE), '200')
        self.assertEqual(span.service, 'test-botocore-tracing.lambda')
        self.assertEqual(span.resource, 'lambda.listfunctions')

    @mock_kms
    def test_kms_client(self):
        kms = self.session.create_client('kms', region_name='us-east-1')
        Pin(service=self.TEST_SERVICE, tracer=self.tracer).onto(kms)

        kms.list_keys(Limit=21)

        spans = self.get_spans()
        assert spans
        span = spans[0]
        self.assertEqual(len(spans), 1)
        self.assertEqual(span.get_tag('aws.region'), 'us-east-1')
        self.assertEqual(span.get_tag('aws.operation'), 'ListKeys')
        self.assertEqual(span.get_tag(http.STATUS_CODE), '200')
        self.assertEqual(span.service, 'test-botocore-tracing.kms')
        self.assertEqual(span.resource, 'kms.listkeys')

        # checking for protection on sts against security leak
        self.assertIsNone(span.get_tag('params'))
