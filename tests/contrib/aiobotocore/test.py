import aiobotocore
from botocore.errorfactory import ClientError

from ddtrace.contrib.aiobotocore.patch import patch, unpatch
from ddtrace.constants import ANALYTICS_SAMPLE_RATE_KEY
from ddtrace.ext import http
from ddtrace.compat import stringify

from .utils import aiobotocore_client
from ..asyncio.utils import AsyncioTestCase, mark_asyncio
from ...test_tracer import get_dummy_tracer


class AIOBotocoreTest(AsyncioTestCase):
    """Botocore integration testsuite"""
    def setUp(self):
        super(AIOBotocoreTest, self).setUp()
        patch()
        self.tracer = get_dummy_tracer()

    def tearDown(self):
        super(AIOBotocoreTest, self).tearDown()
        unpatch()
        self.tracer = None

    @mark_asyncio
    def test_traced_client(self):
        with aiobotocore_client('ec2', self.tracer) as ec2:
            yield from ec2.describe_instances()

        traces = self.tracer.writer.pop_traces()
        self.assertEqual(len(traces), 1)
        self.assertEqual(len(traces[0]), 1)
        span = traces[0][0]

        self.assertEqual(span.get_tag('aws.agent'), 'aiobotocore')
        self.assertEqual(span.get_tag('aws.region'), 'us-west-2')
        self.assertEqual(span.get_tag('aws.operation'), 'DescribeInstances')
        self.assertEqual(span.get_tag('http.status_code'), '200')
        self.assertEqual(span.get_tag('retry_attempts'), '0')
        self.assertEqual(span.service, 'aws.ec2')
        self.assertEqual(span.resource, 'ec2.describeinstances')
        self.assertEqual(span.name, 'ec2.command')
        self.assertEqual(span.span_type, 'http')
        self.assertIsNone(span.get_metric(ANALYTICS_SAMPLE_RATE_KEY))

    @mark_asyncio
    def test_traced_client_analytics(self):
        with self.override_config(
                'aiobotocore',
                dict(analytics_enabled=True, analytics_sample_rate=0.5)
        ):
            with aiobotocore_client('ec2', self.tracer) as ec2:
                yield from ec2.describe_instances()

        spans = self.get_spans()
        assert spans
        span = spans[0]
        self.assertEqual(span.get_metric(ANALYTICS_SAMPLE_RATE_KEY), 0.5)

    @mark_asyncio
    def test_s3_client(self):
        with aiobotocore_client('s3', self.tracer) as s3:
            yield from s3.list_buckets()
            yield from s3.list_buckets()

        traces = self.tracer.writer.pop_traces()
        self.assertEqual(len(traces), 2)
        self.assertEqual(len(traces[0]), 1)
        span = traces[0][0]

        self.assertEqual(span.get_tag('aws.operation'), 'ListBuckets')
        self.assertEqual(span.get_tag('http.status_code'), '200')
        self.assertEqual(span.service, 'aws.s3')
        self.assertEqual(span.resource, 's3.listbuckets')
        self.assertEqual(span.name, 's3.command')

    @mark_asyncio
    def test_s3_put(self):
        params = dict(Key='foo', Bucket='mybucket', Body=b'bar')

        with aiobotocore_client('s3', self.tracer) as s3:
            yield from s3.create_bucket(Bucket='mybucket')
            yield from s3.put_object(**params)

        spans = [trace[0] for trace in self.tracer.writer.pop_traces()]
        assert spans
        self.assertEqual(len(spans), 2)
        self.assertEqual(spans[0].get_tag('aws.operation'), 'CreateBucket')
        self.assertEqual(spans[0].get_tag(http.STATUS_CODE), '200')
        self.assertEqual(spans[0].service, 'aws.s3')
        self.assertEqual(spans[0].resource, 's3.createbucket')
        self.assertEqual(spans[1].get_tag('aws.operation'), 'PutObject')
        self.assertEqual(spans[1].resource, 's3.putobject')
        self.assertEqual(spans[1].get_tag('params.Key'), stringify(params['Key']))
        self.assertEqual(spans[1].get_tag('params.Bucket'), stringify(params['Bucket']))
        self.assertIsNone(spans[1].get_tag('params.Body'))

    @mark_asyncio
    def test_s3_client_error(self):
        with aiobotocore_client('s3', self.tracer) as s3:
            with self.assertRaises(ClientError):
                # FIXME: add proper clean-up to tearDown
                yield from s3.list_objects(Bucket='doesnotexist')

        traces = self.tracer.writer.pop_traces()
        self.assertEqual(len(traces), 1)
        self.assertEqual(len(traces[0]), 1)
        span = traces[0][0]

        self.assertEqual(span.resource, 's3.listobjects')
        self.assertEqual(span.error, 1)
        self.assertTrue('NoSuchBucket' in span.get_tag('error.msg'))

    @mark_asyncio
    def test_s3_client_read(self):
        with aiobotocore_client('s3', self.tracer) as s3:
            # prepare S3 and flush traces if any
            yield from s3.create_bucket(Bucket='tracing')
            yield from s3.put_object(Bucket='tracing', Key='apm', Body=b'')
            self.tracer.writer.pop_traces()
            # calls under test
            response = yield from s3.get_object(Bucket='tracing', Key='apm')
            yield from response['Body'].read()

        traces = self.tracer.writer.pop_traces()
        version = aiobotocore.__version__.split('.')
        pre_08 = int(version[0]) == 0 and int(version[1]) < 8
        if pre_08:
            self.assertEqual(len(traces), 2)
            self.assertEqual(len(traces[1]), 1)
        else:
            self.assertEqual(len(traces), 1)

        self.assertEqual(len(traces[0]), 1)

        span = traces[0][0]
        self.assertEqual(span.get_tag('aws.operation'), 'GetObject')
        self.assertEqual(span.get_tag('http.status_code'), '200')
        self.assertEqual(span.service, 'aws.s3')
        self.assertEqual(span.resource, 's3.getobject')

        if pre_08:
            read_span = traces[1][0]
            self.assertEqual(read_span.get_tag('aws.operation'), 'GetObject')
            self.assertEqual(read_span.get_tag('http.status_code'), '200')
            self.assertEqual(read_span.service, 'aws.s3')
            self.assertEqual(read_span.resource, 's3.getobject')
            self.assertEqual(read_span.name, 's3.command.read')
            # enforce parenting
            self.assertEqual(read_span.parent_id, span.span_id)
            self.assertEqual(read_span.trace_id, span.trace_id)

    @mark_asyncio
    def test_sqs_client(self):
        with aiobotocore_client('sqs', self.tracer) as sqs:
            yield from sqs.list_queues()

        traces = self.tracer.writer.pop_traces()
        self.assertEqual(len(traces), 1)
        self.assertEqual(len(traces[0]), 1)

        span = traces[0][0]
        self.assertEqual(span.get_tag('aws.region'), 'us-west-2')
        self.assertEqual(span.get_tag('aws.operation'), 'ListQueues')
        self.assertEqual(span.get_tag('http.status_code'), '200')
        self.assertEqual(span.service, 'aws.sqs')
        self.assertEqual(span.resource, 'sqs.listqueues')

    @mark_asyncio
    def test_kinesis_client(self):
        with aiobotocore_client('kinesis', self.tracer) as kinesis:
            yield from kinesis.list_streams()

        traces = self.tracer.writer.pop_traces()
        self.assertEqual(len(traces), 1)
        self.assertEqual(len(traces[0]), 1)

        span = traces[0][0]
        self.assertEqual(span.get_tag('aws.region'), 'us-west-2')
        self.assertEqual(span.get_tag('aws.operation'), 'ListStreams')
        self.assertEqual(span.get_tag('http.status_code'), '200')
        self.assertEqual(span.service, 'aws.kinesis')
        self.assertEqual(span.resource, 'kinesis.liststreams')

    @mark_asyncio
    def test_lambda_client(self):
        with aiobotocore_client('lambda', self.tracer) as lambda_client:
            # https://github.com/spulec/moto/issues/906
            yield from lambda_client.list_functions(MaxItems=5)

        traces = self.tracer.writer.pop_traces()
        self.assertEqual(len(traces), 1)
        self.assertEqual(len(traces[0]), 1)

        span = traces[0][0]
        self.assertEqual(span.get_tag('aws.region'), 'us-west-2')
        self.assertEqual(span.get_tag('aws.operation'), 'ListFunctions')
        self.assertEqual(span.get_tag('http.status_code'), '200')
        self.assertEqual(span.service, 'aws.lambda')
        self.assertEqual(span.resource, 'lambda.listfunctions')

    @mark_asyncio
    def test_kms_client(self):
        with aiobotocore_client('kms', self.tracer) as kms:
            yield from kms.list_keys(Limit=21)

        traces = self.tracer.writer.pop_traces()
        self.assertEqual(len(traces), 1)
        self.assertEqual(len(traces[0]), 1)

        span = traces[0][0]
        self.assertEqual(span.get_tag('aws.region'), 'us-west-2')
        self.assertEqual(span.get_tag('aws.operation'), 'ListKeys')
        self.assertEqual(span.get_tag('http.status_code'), '200')
        self.assertEqual(span.service, 'aws.kms')
        self.assertEqual(span.resource, 'kms.listkeys')
        # checking for protection on STS against security leak
        self.assertEqual(span.get_tag('params'), None)

    @mark_asyncio
    def test_unpatch(self):
        unpatch()
        with aiobotocore_client('kinesis', self.tracer) as kinesis:
            yield from kinesis.list_streams()

        traces = self.tracer.writer.pop_traces()
        self.assertEqual(len(traces), 0)

    @mark_asyncio
    def test_double_patch(self):
        patch()
        with aiobotocore_client('sqs', self.tracer) as sqs:
            yield from sqs.list_queues()

        traces = self.tracer.writer.pop_traces()
        self.assertEqual(len(traces), 1)
        self.assertEqual(len(traces[0]), 1)
