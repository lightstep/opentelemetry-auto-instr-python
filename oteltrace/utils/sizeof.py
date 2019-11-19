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

import collections
import sys
from itertools import chain

_UNSET = object()
_DEFAULT_IGNORE_ATTRIBUTES = tuple()


def iter_object(o):
    if hasattr(o, '__slots__'):
        ignore_attributes = getattr(o, '__sizeof_ignore_attributes__', _DEFAULT_IGNORE_ATTRIBUTES)
        return (
            s
            for s in (getattr(o, slot, _UNSET)
                      for slot in o.__slots__
                      if slot not in ignore_attributes)
            if s != _UNSET
        )
    elif hasattr(o, '__dict__'):
        ignore_attributes = getattr(o, '__sizeof_ignore_attributes__', _DEFAULT_IGNORE_ATTRIBUTES)
        return (
            (k, v) for k, v in list(o.__dict__.items())
            if k not in ignore_attributes
        )
    elif isinstance(o, dict):
        # Make a copy to avoid corruption
        return chain.from_iterable(list(o.items()))
    elif isinstance(o, (list, set, frozenset, tuple, collections.deque)):
        # Make a copy to avoid corruption
        return iter(list(o))
    return []


def sizeof(o):
    """Returns the approximate memory footprint an object and all of its contents.

    If an object implements `__sizeof_ignore_attributes__`, those attributes will be ignored when computing the size of
    the object.
    """
    seen = set()

    def _sizeof(o):
        # do not double count the same object
        if id(o) in seen:
            return 0
        seen.add(id(o))
        return sys.getsizeof(o) + sum(map(_sizeof, iter_object(o)))

    return _sizeof(o)
