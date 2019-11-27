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
Bootstrapping code that is run when using the `oteltrace-run` Python entrypoint
Add all monkey-patching that needs to run by default here
"""
import imp
from sys import path
import logging
import importlib
from configparser import ConfigParser
from os.path import join, exists, dirname
from os import environ, getenv
from pathlib import Path
from pkg_resources import iter_entry_points
from inspect import getmodule

from oteltrace import api_otel_exporter
from oteltrace.utils.formats import asbool, get_env
from oteltrace.internal.logger import get_logger
from oteltrace import constants
from oteltrace.propagator.trace_context_propagator import (
    TraceContextPropagator
)
from oteltrace.propagator.datadog_propagator import DatadogPropagator
from oteltrace.propagator.b3_propagator import B3Propagator

log = get_logger(__name__)
configuration_path = join(Path.home(), ".config", "oteltrace_run.cfg")

configuration = ConfigParser(
    defaults={
        "logging": False,
        "deny_patchers": "None",
        "allow_patchers": None,
        "collect_metrics": True,
        "tags": {
            "tag_0": 0,
            "tag_1": 1,
        }
    }
)

if exists(configuration_path):
    try:
        configuration.read(configuration_path)
    except Exception as error:
        log.exception(
            "Unable to load configuration file at {}: {}".format(
                configuration_path, error
            )
        )

configuration = configuration["DEFAULT"]

# FIXME: Check if there is a better way to parse this configuration data:
deny_patchers = set(configuration["deny_patchers"].split(" "))
for patcher_entry_point in iter_entry_points(group="oteltrace_patcher"):

    patcher_entry_point_name = patcher_entry_point.name

    the_error = None
    try:
        patcher_class = patcher_entry_point.load()
    except Exception as error:
        the_error = error
    from traceback import format_tb
    # raise Exception(
    #     the_error, patcher_entry_point_name, format_tb(
    #         the_error.__traceback__
    #     )
    # )

    patcher_module = getmodule(patcher_class)

    if patcher_entry_point_name in deny_patchers:
        log.debug(
            "Plugin {} not patched as requested by configuration".format(
                patcher_entry_point_name
            )
        )
        continue
    try:
        patcher_class().patch()

    except TypeError:
        log.exception(
            "Incomplete interface found in patcher {}".format(
                patcher_entry_point_name
            )
        )

    except Exception as error:
        log.exception(
            "Unable to patch {}: {}".format(
                patcher_entry_point_name, error
            )
        )
        raise


OTEL_LOG_FORMAT = (
    '%(asctime)s %(levelname)s [%(name)s]'
    ' [%(filename)s:%(lineno)d] {}- %(message)s'
)
# DEV: Once basicConfig is called here, future calls to it cannot be used to
# change the formatter since it applies the formatter to the root handler only
# upon initializing it the first time. See:
# https://github.com/python/cpython/blob/112e4afd582515fcdcc0cde5012a4866e5cfda12/Lib/logging/__init__.py#L1550
# if configuration.getboolean("logging"):
#     logging.basicConfig(level=logging.DEBUG, format=OTEL_LOG_FORMAT)
# else:
#     logging.basicConfig(format=OTEL_LOG_FORMAT)

OTEL_MODULE = 'OTEL_EXPORTER_MODULE'
OTEL_FACTORY = 'OTEL_EXPORTER_FACTORY'
OTEL_OPT_PREFIX = 'OTEL_EXPORTER_OPTIONS_'


def get_otel_exporter_options():
    ops = {}

    for var in environ:
        if var.startswith(OTEL_OPT_PREFIX):
            opt_name = var[len(OTEL_OPT_PREFIX):]
            ops[opt_name] = environ.get(var)

    return ops


def load_otel_exporter():
    exporter_module = environ.get(OTEL_MODULE)
    if exporter_module is None:
        log.error('%s is not defined.', OTEL_MODULE)
        return None

    exporter_type = environ.get(OTEL_FACTORY)
    if exporter_type is None:
        log.error('%s is not defined.', OTEL_FACTORY)
        return None

    try:
        otel_module = importlib.import_module(exporter_module)
        otel_callback = getattr(otel_module, exporter_type)
        opt = get_otel_exporter_options()
        return otel_callback(**opt)
    except (ImportError, SyntaxError, AttributeError):
        log.exception('Error creating exporter instance.')
        return None


OTEL_TRACER_PROPAGATOR = 'OTEL_TRACER_PROPAGATOR'
OTEL_TRACER_PROPAGATOR_W3C = 'w3c'
OTEL_TRACER_PROPAGATOR_B3 = 'b3'
OTEL_TRACER_PROPAGATOR_DATADOG = 'datadog'
OTEL_TRACER_PROPAGATOR_DEFAULT = OTEL_TRACER_PROPAGATOR_W3C

OTEL_TRACER_PROPAGATOR_MAP = {
    OTEL_TRACER_PROPAGATOR_W3C: TraceContextPropagator,
    OTEL_TRACER_PROPAGATOR_B3: B3Propagator,
    OTEL_TRACER_PROPAGATOR_DATADOG: DatadogPropagator,
}


def get_http_propagator_factory():
    """Returns an http propagator factory based on set env variables"""
    prop = getenv(OTEL_TRACER_PROPAGATOR, OTEL_TRACER_PROPAGATOR_DEFAULT)
    return OTEL_TRACER_PROPAGATOR_MAP[prop.lower()]
