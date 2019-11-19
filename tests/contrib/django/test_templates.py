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

# 3rd party
from django.template import Context, Template

# testing
from .utils import DjangoTraceTestCase, override_oteltrace_settings


class DjangoTemplateTest(DjangoTraceTestCase):
    """
    Ensures that the template system is properly traced
    """
    def test_template(self):
        # prepare a base template using the default engine
        template = Template('Hello {{name}}!')
        ctx = Context({'name': 'Django'})

        # (trace) the template rendering
        start = time.time()
        assert template.render(ctx) == 'Hello Django!'
        end = time.time()

        # tests
        spans = self.tracer.writer.pop()
        assert spans, spans
        assert len(spans) == 1

        span = spans[0]
        assert span.span_type == 'template'
        assert span.name == 'django.template'
        assert span.get_tag('django.template_name') == 'unknown'
        assert start < span.start < span.start + span.duration < end

    @override_oteltrace_settings(INSTRUMENT_TEMPLATE=False)
    def test_template_disabled(self):
        # prepare a base template using the default engine
        template = Template('Hello {{name}}!')
        ctx = Context({'name': 'Django'})

        # (trace) the template rendering
        assert template.render(ctx) == 'Hello Django!'

        # tests
        spans = self.tracer.writer.pop()
        assert len(spans) == 0
