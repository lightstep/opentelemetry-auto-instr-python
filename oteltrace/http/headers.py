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

import re

from ..internal.logger import get_logger
from ..utils.http import normalize_header_name

log = get_logger(__name__)

REQUEST = 'request'
RESPONSE = 'response'

# Tag normalization based on: https://docs.datadoghq.com/tagging/#defining-tags
# With the exception of '.' in header names which are replaced with '_' to avoid
# starting a "new object" on the UI.
NORMALIZE_PATTERN = re.compile(r'([^a-z0-9_\-:/]){1}')


def store_request_headers(headers, span, integration_config):
    """
    Store request headers as a span's tags
    :param headers: All the request's http headers, will be filtered through the whitelist
    :type headers: dict or list
    :param span: The Span instance where tags will be stored
    :type span: oteltrace.Span
    :param integration_config: An integration specific config object.
    :type integration_config: oteltrace.settings.IntegrationConfig
    """
    _store_headers(headers, span, integration_config, REQUEST)


def store_response_headers(headers, span, integration_config):
    """
    Store response headers as a span's tags
    :param headers: All the response's http headers, will be filtered through the whitelist
    :type headers: dict or list
    :param span: The Span instance where tags will be stored
    :type span: oteltrace.Span
    :param integration_config: An integration specific config object.
    :type integration_config: oteltrace.settings.IntegrationConfig
    """
    _store_headers(headers, span, integration_config, RESPONSE)


def _store_headers(headers, span, integration_config, request_or_response):
    """
    :param headers: A dict of http headers to be stored in the span
    :type headers: dict or list
    :param span: The Span instance where tags will be stored
    :type span: oteltrace.span.Span
    :param integration_config: An integration specific config object.
    :type integration_config: oteltrace.settings.IntegrationConfig
    """
    if not isinstance(headers, dict):
        try:
            headers = dict(headers)
        except Exception:
            return

    if integration_config is None:
        log.debug('Skipping headers tracing as no integration config was provided')
        return

    for header_name, header_value in headers.items():
        if not integration_config.header_is_traced(header_name):
            continue
        tag_name = _normalize_tag_name(request_or_response, header_name)
        span.set_tag(tag_name, header_value)


def _normalize_tag_name(request_or_response, header_name):
    """
    Given a tag name, e.g. 'Content-Type', returns a corresponding normalized tag name, i.e
    'http.request.headers.content_type'. Rules applied actual header name are:
       - any letter is converted to lowercase
       - any digit is left unchanged
       - any block of any length of different ASCII chars is converted to a single underscore '_'
    :param request_or_response: The context of the headers: request|response
    :param header_name: The header's name
    :type header_name: str
    :rtype: str
    """
    # Looking at:
    #   - http://www.iana.org/assignments/message-headers/message-headers.xhtml
    #   - https://tools.ietf.org/html/rfc6648
    # and for consistency with other language integrations seems safe to assume the following algorithm for header
    # names normalization:
    #   - any letter is converted to lowercase
    #   - any digit is left unchanged
    #   - any block of any length of different ASCII chars is converted to a single underscore '_'
    normalized_name = NORMALIZE_PATTERN.sub('_', normalize_header_name(header_name))
    return 'http.{}.headers.{}'.format(request_or_response, normalized_name)
