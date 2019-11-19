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

import os
import sys


if __name__ == '__main__':
    # define django defaults
    app_to_test = 'tests/contrib/django'

    # append the project root to the PYTHONPATH:
    # this is required because we don't want to put the current file
    # in the project_root
    current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    project_root = os.path.join(current_dir, '..', '..')
    sys.path.append(project_root)

    from django.core.management import execute_from_command_line
    execute_from_command_line([sys.argv[0], 'test', app_to_test])
