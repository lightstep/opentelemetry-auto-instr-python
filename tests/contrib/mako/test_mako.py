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

import os.path
import unittest

# 3rd party
from mako.template import Template
from mako.lookup import TemplateLookup
from mako.runtime import Context

from oteltrace import Pin
from oteltrace.contrib.mako import patch, unpatch
from oteltrace.compat import StringIO, to_unicode
from tests.test_tracer import get_dummy_tracer

TEST_DIR = os.path.dirname(os.path.realpath(__file__))
TMPL_DIR = os.path.join(TEST_DIR, 'templates')


class MakoTest(unittest.TestCase):
    def setUp(self):
        patch()
        self.tracer = get_dummy_tracer()
        Pin.override(Template, tracer=self.tracer)

    def tearDown(self):
        unpatch()

    def test_render(self):
        # render
        t = Template('Hello ${name}!')
        self.assertEqual(t.render(name='mako'), 'Hello mako!')

        spans = self.tracer.writer.pop()
        self.assertEqual(len(spans), 1)

        self.assertEqual(spans[0].service, 'mako')
        self.assertEqual(spans[0].span_type, 'template')
        self.assertEqual(spans[0].get_tag('mako.template_name'), '<memory>')
        self.assertEqual(spans[0].name, 'mako.template.render')
        self.assertEqual(spans[0].resource, '<memory>')

        # render_unicode
        t = Template('Hello ${name}!')
        self.assertEqual(t.render_unicode(name='mako'), to_unicode('Hello mako!'))
        spans = self.tracer.writer.pop()
        self.assertEqual(len(spans), 1)
        self.assertEqual(spans[0].service, 'mako')
        self.assertEqual(spans[0].span_type, 'template')
        self.assertEqual(spans[0].get_tag('mako.template_name'), '<memory>')
        self.assertEqual(spans[0].name, 'mako.template.render_unicode')
        self.assertEqual(spans[0].resource, '<memory>')

        # render_context
        t = Template('Hello ${name}!')
        buf = StringIO()
        c = Context(buf, name='mako')
        t.render_context(c)
        self.assertEqual(buf.getvalue(), 'Hello mako!')
        spans = self.tracer.writer.pop()
        self.assertEqual(len(spans), 1)
        self.assertEqual(spans[0].service, 'mako')
        self.assertEqual(spans[0].span_type, 'template')
        self.assertEqual(spans[0].get_tag('mako.template_name'), '<memory>')
        self.assertEqual(spans[0].name, 'mako.template.render_context')
        self.assertEqual(spans[0].resource, '<memory>')

    def test_file_template(self):
        tmpl_lookup = TemplateLookup(directories=[TMPL_DIR])
        t = tmpl_lookup.get_template('template.html')
        self.assertEqual(t.render(name='mako'), 'Hello mako!\n')

        spans = self.tracer.writer.pop()
        self.assertEqual(len(spans), 1)

        template_name = os.path.join(TMPL_DIR, 'template.html')

        self.assertEqual(spans[0].span_type, 'template')
        self.assertEqual(spans[0].service, 'mako')
        self.assertEqual(spans[0].get_tag('mako.template_name'), template_name)
        self.assertEqual(spans[0].name, 'mako.template.render')
        self.assertEqual(spans[0].resource, template_name)
