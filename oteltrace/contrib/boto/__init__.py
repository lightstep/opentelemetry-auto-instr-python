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
Boto integration will trace all AWS calls made via boto2.
This integration is automatically patched when using ``patch_all()``::

    import boto.ec2
    from oteltrace import patch

    # If not patched yet, you can patch boto specifically
    patch(boto=True)

    # This will report spans with the default instrumentation
    ec2 = boto.ec2.connect_to_region("us-west-2")
    # Example of instrumented query
    ec2.get_all_instances()
"""

from ...utils.importlib import require_modules

required_modules = ['boto.connection']

with require_modules(required_modules) as missing_modules:
    if not missing_modules:
        from .patch import patch
        __all__ = ['patch']
