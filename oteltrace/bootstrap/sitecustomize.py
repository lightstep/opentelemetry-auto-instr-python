"""
Bootstrapping code that is run when using the `oteltrace-run` Python entrypoint
Add all monkey-patching that needs to run by default here
"""

import os
import imp
import sys
import logging

from oteltrace.utils.formats import asbool, get_env
from oteltrace.internal.logger import get_logger

logs_injection = asbool(get_env('logs', 'injection'))
OTEL_LOG_FORMAT = '%(asctime)s %(levelname)s [%(name)s] [%(filename)s:%(lineno)d] {}- %(message)s'.format(
    '[dd.trace_id=%(dd.trace_id)s dd.span_id=%(dd.span_id)s] ' if logs_injection else ''
)

if logs_injection:
    # immediately patch logging if trace id injected
    from oteltrace import patch
    patch(logging=True)

debug = os.environ.get('OPENTELEMETRY_TRACE_DEBUG')

# Set here a default logging format for basicConfig

# DEV: Once basicConfig is called here, future calls to it cannot be used to
# change the formatter since it applies the formatter to the root handler only
# upon initializing it the first time.
# See https://github.com/python/cpython/blob/112e4afd582515fcdcc0cde5012a4866e5cfda12/Lib/logging/__init__.py#L1550
if debug and debug.lower() == 'true':
    logging.basicConfig(level=logging.DEBUG, format=OTEL_LOG_FORMAT)
else:
    logging.basicConfig(format=OTEL_LOG_FORMAT)

log = get_logger(__name__)

EXTRA_PATCHED_MODULES = {
    'bottle': True,
    'django': True,
    'falcon': True,
    'flask': True,
    'pylons': True,
    'pyramid': True,
}


def update_patched_modules():
    modules_to_patch = os.environ.get('OPENTELEMETRY_PATCH_MODULES')
    if not modules_to_patch:
        return
    for patch in modules_to_patch.split(','):
        if len(patch.split(':')) != 2:
            log.debug('skipping malformed patch instruction')
            continue

        module, should_patch = patch.split(':')
        if should_patch.lower() not in ['true', 'false']:
            log.debug('skipping malformed patch instruction for %s', module)
            continue

        EXTRA_PATCHED_MODULES.update({module: should_patch.lower() == 'true'})


def add_global_tags(tracer):
    tags = {}
    for tag in os.environ.get('OTEL_TRACE_GLOBAL_TAGS', '').split(','):
        tag_name, _, tag_value = tag.partition(':')
        if not tag_name or not tag_value:
            log.debug('skipping malformed tracer tag')
            continue

        tags[tag_name] = tag_value
    tracer.set_tags(tags)


try:
    from oteltrace import tracer
    patch = True

    # Respect OPENTELEMETRY_* environment variables in global tracer configuration
    # TODO: these variables are deprecated; use utils method and update our documentation
    # correct prefix should be OTEL_*
    enabled = os.environ.get('OPENTELEMETRY_TRACE_ENABLED')
    priority_sampling = os.environ.get('OPENTELEMETRY_PRIORITY_SAMPLING')
    opts = {}

    if enabled and enabled.lower() == 'false':
        opts['enabled'] = False
        patch = False
    if priority_sampling:
        opts['priority_sampling'] = asbool(priority_sampling)

    opts['collect_metrics'] = asbool(get_env('runtime_metrics', 'enabled'))

    if opts:
        tracer.configure(**opts)

    if logs_injection:
        EXTRA_PATCHED_MODULES.update({'logging': True})

    if patch:
        update_patched_modules()
        from oteltrace import patch_all
        patch_all(**EXTRA_PATCHED_MODULES)

    debug = os.environ.get('OPENTELEMETRY_TRACE_DEBUG')
    if debug and debug.lower() == 'true':
        tracer.debug_logging = True

    if 'OPENTELEMETRY_ENV' in os.environ:
        tracer.set_tags({'env': os.environ['OPENTELEMETRY_ENV']})

    if 'OTEL_TRACE_GLOBAL_TAGS' in os.environ:
        add_global_tags(tracer)

    # Ensure sitecustomize.py is properly called if available in application directories:
    # * exclude `bootstrap_dir` from the search
    # * find a user `sitecustomize.py` module
    # * import that module via `imp`
    bootstrap_dir = os.path.dirname(__file__)
    path = list(sys.path)

    if bootstrap_dir in path:
        path.remove(bootstrap_dir)

    try:
        (f, path, description) = imp.find_module('sitecustomize', path)
    except ImportError:
        pass
    else:
        # `sitecustomize.py` found, load it
        log.debug('sitecustomize from user found in: %s', path)
        imp.load_module('sitecustomize', f, path, description)

    # Loading status used in tests to detect if the `sitecustomize` has been
    # properly loaded without exceptions. This must be the last action in the module
    # when the execution ends with a success.
    loaded = True
except Exception:
    loaded = False
    log.warning('error configuring OpenTelemetry tracing', exc_info=True)
