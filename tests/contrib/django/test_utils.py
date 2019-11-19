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

# 3d party
from django.test import TestCase

# project
from oteltrace.contrib.django.utils import quantize_key_values


class DjangoUtilsTest(TestCase):
    def test_quantize_key_values(self):
        """
        Ensure that the utility functions properly convert a dictionary object
        """
        key = {'second_key': 2, 'first_key': 1}
        result = quantize_key_values(key)
        assert len(result) == 2
        assert 'first_key' in result
        assert 'second_key' in result
