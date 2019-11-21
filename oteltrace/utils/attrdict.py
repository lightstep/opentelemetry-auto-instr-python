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


class AttrDict(dict):
    """
    dict implementation that allows for item attribute access


    Example::

       data = AttrDict()
       data['key'] = 'value'
       print(data['key'])

       data.key = 'new-value'
       print(data.key)

       # Convert an existing `dict`
       data = AttrDict(dict(key='value'))
       print(data.key)
    """

    def __getattr__(self, key):
        if key in self:
            return self[key]
        return object.__getattribute__(self, key)

    def __setattr__(self, key, value):
        # 1) Ensure if the key exists from a dict key we always prefer that
        # 2) If we do not have an existing key but we do have an attr, set that
        # 3) No existing key or attr exists, so set a key
        if key in self:
            # Update any existing key
            self[key] = value
        elif hasattr(self, key):
            # Allow overwriting an existing attribute, e.g. `self.global_config = dict()`
            object.__setattr__(self, key, value)
        else:
            # Set a new key
            self[key] = value
