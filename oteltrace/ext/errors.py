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
tags for common error attributes
"""

import traceback


ERROR_MSG = 'error.msg'  # a string representing the error message
ERROR_TYPE = 'error.type'  # a string representing the type of the error
ERROR_STACK = 'error.stack'  # a human readable version of the stack. beta.

# shorthand for -----^
MSG = ERROR_MSG
TYPE = ERROR_TYPE
STACK = ERROR_STACK


def get_traceback(tb=None, error=None):
    t = None
    if error:
        t = type(error)
    lines = traceback.format_exception(t, error, tb, limit=20)
    return '\n'.join(lines)
