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

from oteltrace.vendor import wrapt
import inspect

from .deprecation import deprecated


def unwrap(obj, attr):
    f = getattr(obj, attr, None)
    if f and isinstance(f, wrapt.ObjectProxy) and hasattr(f, '__wrapped__'):
        setattr(obj, attr, f.__wrapped__)


@deprecated('`wrapt` library is used instead', version='1.0.0')
def safe_patch(patchable, key, patch_func, service, meta, tracer):
    """ takes patch_func (signature: takes the orig_method that is
    wrapped in the monkey patch == UNBOUND + service and meta) and
    attach the patched result to patchable at patchable.key


      - if this is the module/class we can rely on methods being unbound, and just have to
      update the __dict__

      - if this is an instance, we have to unbind the current and rebind our
      patched method

      - If patchable is an instance and if we've already patched at the module/class level
      then patchable[key] contains an already patched command!
      To workaround this, check if patchable or patchable.__class__ are _dogtraced
      If is isn't, nothing to worry about, patch the key as usual
      But if it is, search for a '__otel_orig_{key}' method on the class, which is
      the original unpatched method we wish to trace.

    """
    def _get_original_method(thing, key):
        orig = None
        if hasattr(thing, '_dogtraced'):
            # Search for original method
            orig = getattr(thing, '__otel_orig_{}'.format(key), None)
        else:
            orig = getattr(thing, key)
            # Set it for the next time we attempt to patch `thing`
            setattr(thing, '__otel_orig_{}'.format(key), orig)

        return orig

    if inspect.isclass(patchable) or inspect.ismodule(patchable):
        orig = _get_original_method(patchable, key)
        if not orig:
            # Should never happen
            return
    elif hasattr(patchable, '__class__'):
        orig = _get_original_method(patchable.__class__, key)
        if not orig:
            # Should never happen
            return
    else:
        return

    dest = patch_func(orig, service, meta, tracer)

    if inspect.isclass(patchable) or inspect.ismodule(patchable):
        setattr(patchable, key, dest)
    elif hasattr(patchable, '__class__'):
        setattr(patchable, key, dest.__get__(patchable, patchable.__class__))
