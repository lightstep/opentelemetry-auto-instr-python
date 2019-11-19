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

# https://stackoverflow.com/a/26853961
def merge_dicts(x, y):
    """Returns a copy of y merged into x."""
    z = x.copy()  # start with x's keys and values
    z.update(y)  # modifies z with y's keys and values & returns None
    return z


def get_module_name(module):
    """Returns a module's name or None if one cannot be found.
    Relevant PEP: https://www.python.org/dev/peps/pep-0451/
    """
    if hasattr(module, '__spec__'):
        return module.__spec__.name
    return getattr(module, '__name__', None)
