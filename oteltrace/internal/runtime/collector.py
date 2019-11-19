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

import importlib

from ..logger import get_logger

log = get_logger(__name__)


class ValueCollector(object):
    """A basic state machine useful for collecting, caching and updating data
    obtained from different Python modules.

    The two primary use-cases are
    1) data loaded once (like tagging information)
    2) periodically updating data sources (like thread count)

    Functionality is provided for requiring and importing modules which may or
    may not be installed.
    """
    enabled = True
    periodic = False
    required_modules = []
    value = None
    value_loaded = False

    def __init__(self, enabled=None, periodic=None, required_modules=None):
        self.enabled = self.enabled if enabled is None else enabled
        self.periodic = self.periodic if periodic is None else periodic
        self.required_modules = self.required_modules if required_modules is None else required_modules

        self._modules_successfully_loaded = False
        self.modules = self._load_modules()
        if self._modules_successfully_loaded:
            self._on_modules_load()

    def _on_modules_load(self):
        """Hook triggered after all required_modules have been successfully loaded.
        """

    def _load_modules(self):
        modules = {}
        try:
            for module in self.required_modules:
                modules[module] = importlib.import_module(module)
            self._modules_successfully_loaded = True
        except ImportError:
            # DEV: disable collector if we cannot load any of the required modules
            self.enabled = False
            log.warning('Could not import module "{}" for {}. Disabling collector.'.format(module, self))
            return None
        return modules

    def collect(self, keys=None):
        """Returns metrics as collected by `collect_fn`.

        :param keys: The keys of the metrics to collect.
        """
        if not self.enabled:
            return self.value

        keys = keys or set()

        if not self.periodic and self.value_loaded:
            return self.value

        # call underlying collect function and filter out keys not requested
        self.value = self.collect_fn(keys)

        # filter values for keys
        if len(keys) > 0 and isinstance(self.value, list):
            self.value = [
                (k, v)
                for (k, v) in self.value
                if k in keys
            ]

        self.value_loaded = True
        return self.value

    def __repr__(self):
        return '<{}(enabled={},periodic={},required_modules={})>'.format(
            self.__class__.__name__,
            self.enabled,
            self.periodic,
            self.required_modules,
        )
