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

from ..internal.logger import get_logger
from ..utils.http import normalize_header_name

log = get_logger(__name__)


class HttpConfig(object):
    """
    Configuration object that expose an API to set and retrieve both global and integration specific settings
    related to the http context.
    """

    def __init__(self):
        self._whitelist_headers = set()
        self.trace_query_string = None

    @property
    def is_header_tracing_configured(self):
        return len(self._whitelist_headers) > 0

    def trace_headers(self, whitelist):
        """
        Registers a set of headers to be traced at global level or integration level.
        :param whitelist: the case-insensitive list of traced headers
        :type whitelist: list of str or str
        :return: self
        :rtype: HttpConfig
        """
        if not whitelist:
            return

        whitelist = [whitelist] if isinstance(whitelist, str) else whitelist
        for whitelist_entry in whitelist:
            normalized_header_name = normalize_header_name(whitelist_entry)
            if not normalized_header_name:
                continue
            self._whitelist_headers.add(normalized_header_name)

        return self

    def header_is_traced(self, header_name):
        """
        Returns whether or not the current header should be traced.
        :param header_name: the header name
        :type header_name: str
        :rtype: bool
        """
        normalized_header_name = normalize_header_name(header_name)
        log.debug('Checking header \'%s\' tracing in whitelist %s', normalized_header_name, self._whitelist_headers)
        return normalized_header_name in self._whitelist_headers

    def __repr__(self):
        return '<{} traced_headers={} trace_query_string={}>'.format(
            self.__class__.__name__, self._whitelist_headers, self.trace_query_string)
