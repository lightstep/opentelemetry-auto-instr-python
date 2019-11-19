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
Standard http tags.

For example:

span.set_tag(URL, '/user/home')
span.set_tag(STATUS_CODE, 404)
"""

# type of the spans
TYPE = 'http'

# tags
URL = 'http.url'
METHOD = 'http.method'
STATUS_CODE = 'http.status_code'
QUERY_STRING = 'http.query.string'

# template render span type
TEMPLATE = 'template'


def normalize_status_code(code):
    return code.split(' ')[0]
