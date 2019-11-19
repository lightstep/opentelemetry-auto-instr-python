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

# project
from oteltrace.contrib.django.conf import OpenTelemetrySettings

# testing
from .utils import DjangoTraceTestCase


class DjangoInstrumentationTest(DjangoTraceTestCase):
    """
    Ensures that Django is correctly configured according to
    users settings
    """
    def test_tracer_flags(self):
        assert self.tracer.enabled
        assert self.tracer.tags == {'env': 'test'}

    def test_environment_vars(self):
        # Django defaults can be overridden by env vars, ensuring that
        # environment strings are properly converted
        with self.override_env(dict(
            OPENTELEMETRY_TRACE_AGENT_HOSTNAME='agent.consul.local',
            OPENTELEMETRY_TRACE_AGENT_PORT='58126'
        )):
            settings = OpenTelemetrySettings()
            assert settings.AGENT_HOSTNAME == 'agent.consul.local'
            assert settings.AGENT_PORT == 58126

    def test_environment_var_wrong_port(self):
        # ensures that a wrong Agent Port doesn't crash the system
        # and defaults to 8126
        with self.override_env(dict(OPENTELEMETRY_TRACE_AGENT_PORT='something')):
            settings = OpenTelemetrySettings()
            assert settings.AGENT_PORT == 8126
