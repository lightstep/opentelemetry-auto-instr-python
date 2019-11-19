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
The aiobotocore integration will trace all AWS calls made with the ``aiobotocore``
library. This integration isn't enabled when applying the default patching.
To enable it, you must run ``patch_all(aiobotocore=True)``

::

    import aiobotocore.session
    from oteltrace import patch

    # If not patched yet, you can patch botocore specifically
    patch(aiobotocore=True)

    # This will report spans with the default instrumentation
    aiobotocore.session.get_session()
    lambda_client = session.create_client('lambda', region_name='us-east-1')

    # This query generates a trace
    lambda_client.list_functions()
"""
from ...utils.importlib import require_modules


required_modules = ["aiobotocore.client"]

with require_modules(required_modules) as missing_modules:
    if not missing_modules:
        from .patch import patch

        __all__ = ["patch"]
