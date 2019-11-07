#!/usr/bin/env python
from distutils import spawn
import os
import sys
import logging

debug = os.environ.get('OPENTELEMETRY_TRACE_DEBUG')
if debug and debug.lower() == 'true':
    logging.basicConfig(level=logging.DEBUG)

# Do not use `oteltrace.internal.logger.get_logger` here
# DEV: It isn't really necessary to use `OtelLogger` here so we want to
#        defer importing `oteltrace` until we actually need it.
#      As well, no actual rate limiting would apply here since we only
#        have a few logged lines
log = logging.getLogger(__name__)

USAGE = """
Execute the given Python program after configuring it to emit OpenTelemetry traces.
Append command line arguments to your program as usual.

Usage: [ENV_VARS] oteltrace-run <my_program>

Available environment variables:

    OPENTELEMETRY_ENV : override an application's environment (no default)
    OPENTELEMETRY_TRACE_ENABLED=true|false : override the value of tracer.enabled (default: true)
    OPENTELEMETRY_TRACE_DEBUG=true|false : enabled debug logging (default: false)
    OPENTELEMETRY_PATCH_MODULES=module:patch,module:patch... e.g. boto:true,redis:false : override the modules patched for this execution of the program (default: none)
    OPENTELEMETRY_SERVICE_NAME : override the service name to be used for this program (no default)
                           This value is passed through when setting up middleware for web framework integrations.
                           (e.g. pylons, flask, django)
                           For tracing without a web integration, prefer setting the service name in code.
    OPENTELEMETRY_PRIORITY_SAMPLING=true|false : (default: false): enables Priority Sampling.
"""  # noqa: E501


def _oteltrace_root():
    from oteltrace import __file__
    return os.path.dirname(__file__)


def _add_bootstrap_to_pythonpath(bootstrap_dir):
    """
    Add our bootstrap directory to the head of $PYTHONPATH to ensure
    it is loaded before program code
    """
    python_path = os.environ.get('PYTHONPATH', '')

    if python_path:
        new_path = '%s%s%s' % (bootstrap_dir, os.path.pathsep, os.environ['PYTHONPATH'])
        os.environ['PYTHONPATH'] = new_path
    else:
        os.environ['PYTHONPATH'] = bootstrap_dir


def main():
    if len(sys.argv) < 2 or sys.argv[1] == '-h':
        print(USAGE)
        return

    log.debug('sys.argv: %s', sys.argv)

    root_dir = _oteltrace_root()
    log.debug('oteltrace root: %s', root_dir)

    bootstrap_dir = os.path.join(root_dir, 'bootstrap')
    log.debug('oteltrace bootstrap: %s', bootstrap_dir)

    _add_bootstrap_to_pythonpath(bootstrap_dir)
    log.debug('PYTHONPATH: %s', os.environ['PYTHONPATH'])
    log.debug('sys.path: %s', sys.path)

    executable = sys.argv[1]

    # Find the executable path
    executable = spawn.find_executable(executable)
    log.debug('program executable: %s', executable)

    os.execl(executable, executable, *sys.argv[2:])
