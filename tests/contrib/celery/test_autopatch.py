#!/usr/bin/env python
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

import subprocess
import unittest


class DdtraceRunTest(unittest.TestCase):
    """Test that celery is patched successfully if run with oteltrace-run."""

    def test_autopatch(self):
        out = subprocess.check_output(
            ['oteltrace-run', 'python', 'tests/contrib/celery/autopatch.py']
        )
        assert out.startswith(b'Test success')
