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

import logging

if __name__ == '__main__':
    # Ensure if module is patched then default log formatter is set up for logs
    if getattr(logging, '_opentelemetry_patch'):
        assert '[otel.trace_id=%(otel.trace_id)s otel.span_id=%(otel.span_id)s]' in \
            logging.root.handlers[0].formatter._fmt
    else:
        assert '[otel.trace_id=%(otel.trace_id)s otel.span_id=%(otel.span_id)s]' not in \
            logging.root.handlers[0].formatter._fmt
    print('Test success')
