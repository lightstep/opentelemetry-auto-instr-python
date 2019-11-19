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
The Algoliasearch__ integration will add tracing to your Algolia searches.

::

    from oteltrace import patch_all
    patch_all()

    from algoliasearch import algoliasearch
    client = alogliasearch.Client(<ID>, <API_KEY>)
    index = client.init_index(<INDEX_NAME>)
    index.search("your query", args={"attributesToRetrieve": "attribute1,attribute1"})

Configuration
~~~~~~~~~~~~~

.. py:data:: oteltrace.config.algoliasearch['collect_query_text']

   Whether to pass the text of your query onto OpenTelemetry. Since this may contain sensitive data it's off by default

   Default: ``False``

.. __: https://www.algolia.com
"""

from ...utils.importlib import require_modules

with require_modules(['algoliasearch', 'algoliasearch.version']) as missing_modules:
    if not missing_modules:
        from .patch import patch, unpatch

        __all__ = ['patch', 'unpatch']
