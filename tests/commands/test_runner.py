import os
import subprocess
import sys

from ..base import BaseTestCase


def inject_sitecustomize(path):
    """Creates a new environment, injecting a ``sitecustomize.py`` module in
    the current PYTHONPATH.

    :param path: package path containing ``sitecustomize.py`` module, starting
                 from the oteltrace root folder
    :returns: a cloned environment that includes an altered PYTHONPATH with
              the given `sitecustomize.py`
    """
    from oteltrace import __file__ as root_file
    root_folder = os.path.dirname(root_file)
    # Copy the current environment and replace the PYTHONPATH. This is
    # required otherwise `oteltrace` scripts are not found when `env` kwarg is
    # passed
    env = os.environ.copy()
    sitecustomize = os.path.join(root_folder, '..', path)

    # Add `boostrap` module so that `sitecustomize.py` is at the bottom
    # of the PYTHONPATH
    python_path = list(sys.path) + [sitecustomize]
    env['PYTHONPATH'] = ':'.join(python_path)[1:]
    return env


class OteltraceRunTest(BaseTestCase):
    def test_service_name_passthrough(self):
        """
        $OPENTELEMETRY_SERVICE_NAME gets passed through to the program
        """
        with self.override_env(dict(OPENTELEMETRY_SERVICE_NAME='my_test_service')):
            out = subprocess.check_output(
                ['oteltrace-run', 'python', 'tests/commands/oteltrace_run_service.py']
            )
            assert out.startswith(b'Test success')

    def test_env_name_passthrough(self):
        """
        $OPENTELEMETRY_ENV gets passed through to the global tracer as an 'env' tag
        """
        with self.override_env(dict(OPENTELEMETRY_ENV='test')):
            out = subprocess.check_output(
                ['oteltrace-run', 'python', 'tests/commands/oteltrace_run_env.py']
            )
            assert out.startswith(b'Test success')

    def test_env_enabling(self):
        """
        OPENTELEMETRY_TRACE_ENABLED=false allows disabling of the global tracer
        """
        with self.override_env(dict(OPENTELEMETRY_TRACE_ENABLED='false')):
            out = subprocess.check_output(
                ['oteltrace-run', 'python', 'tests/commands/oteltrace_run_disabled.py']
            )
            assert out.startswith(b'Test success')

        with self.override_env(dict(OPENTELEMETRY_TRACE_ENABLED='true')):
            out = subprocess.check_output(
                ['oteltrace-run', 'python', 'tests/commands/oteltrace_run_enabled.py']
            )
            assert out.startswith(b'Test success')

    def test_patched_modules(self):
        """
        Using `oteltrace-run` registers some generic patched modules
        """
        out = subprocess.check_output(
            ['oteltrace-run', 'python', 'tests/commands/oteltrace_run_patched_modules.py']
        )
        assert out.startswith(b'Test success')

    def test_integration(self):
        out = subprocess.check_output(
            ['oteltrace-run', 'python', '-m', 'tests.commands.oteltrace_run_integration']
        )
        assert out.startswith(b'Test success')

    def test_debug_enabling(self):
        """
        OPENTELEMETRY_TRACE_DEBUG=true allows setting debug logging of the global tracer
        """
        with self.override_env(dict(OPENTELEMETRY_TRACE_DEBUG='false')):
            out = subprocess.check_output(
                ['oteltrace-run', 'python', 'tests/commands/oteltrace_run_no_debug.py']
            )
            assert out.startswith(b'Test success')

        with self.override_env(dict(OPENTELEMETRY_TRACE_DEBUG='true')):
            out = subprocess.check_output(
                ['oteltrace-run', 'python', 'tests/commands/oteltrace_run_debug.py']
            )
            assert out.startswith(b'Test success')

    def test_priority_sampling_from_env(self):
        """
        OPENTELEMETRY_PRIORITY_SAMPLING enables Distributed Sampling
        """
        with self.override_env(dict(OPENTELEMETRY_PRIORITY_SAMPLING='True')):
            out = subprocess.check_output(
                ['oteltrace-run', 'python', 'tests/commands/oteltrace_run_priority_sampling.py']
            )
            assert out.startswith(b'Test success')

    def test_patch_modules_from_env(self):
        """
        OPENTELEMETRY_PATCH_MODULES overrides the defaults for patch_all()
        """
        from oteltrace.bootstrap.sitecustomize import EXTRA_PATCHED_MODULES, update_patched_modules
        orig = EXTRA_PATCHED_MODULES.copy()

        # empty / malformed strings are no-ops
        with self.override_env(dict(OPENTELEMETRY_PATCH_MODULES='')):
            update_patched_modules()
            assert orig == EXTRA_PATCHED_MODULES

        with self.override_env(dict(OPENTELEMETRY_PATCH_MODULES=':')):
            update_patched_modules()
            assert orig == EXTRA_PATCHED_MODULES

        with self.override_env(dict(OPENTELEMETRY_PATCH_MODULES=',')):
            update_patched_modules()
            assert orig == EXTRA_PATCHED_MODULES

        with self.override_env(dict(OPENTELEMETRY_PATCH_MODULES=',:')):
            update_patched_modules()
            assert orig == EXTRA_PATCHED_MODULES

        # overrides work in either direction
        with self.override_env(dict(OPENTELEMETRY_PATCH_MODULES='django:false')):
            update_patched_modules()
            assert EXTRA_PATCHED_MODULES['django'] is False

        with self.override_env(dict(OPENTELEMETRY_PATCH_MODULES='boto:true')):
            update_patched_modules()
            assert EXTRA_PATCHED_MODULES['boto'] is True

        with self.override_env(dict(OPENTELEMETRY_PATCH_MODULES='django:true,boto:false')):
            update_patched_modules()
            assert EXTRA_PATCHED_MODULES['boto'] is False
            assert EXTRA_PATCHED_MODULES['django'] is True

        with self.override_env(dict(OPENTELEMETRY_PATCH_MODULES='django:false,boto:true')):
            update_patched_modules()
            assert EXTRA_PATCHED_MODULES['boto'] is True
            assert EXTRA_PATCHED_MODULES['django'] is False

    def test_sitecustomize_without_oteltrace_run_command(self):
        # [Regression test]: ensure `sitecustomize` path is removed only if it's
        # present otherwise it will cause:
        #   ValueError: list.remove(x): x not in list
        # as mentioned here: https://github.com/opentelemetry/otel-trace-py/pull/516
        env = inject_sitecustomize('')
        out = subprocess.check_output(
            ['python', 'tests/commands/oteltrace_minimal.py'],
            env=env,
        )
        # `out` contains the `loaded` status of the module
        result = out[:-1] == b'True'
        self.assertTrue(result)

    def test_sitecustomize_run(self):
        # [Regression test]: ensure users `sitecustomize.py` is properly loaded,
        # so that our `bootstrap/sitecustomize.py` doesn't override the one
        # defined in users' PYTHONPATH.
        env = inject_sitecustomize('tests/commands/bootstrap')
        out = subprocess.check_output(
            ['oteltrace-run', 'python', 'tests/commands/oteltrace_run_sitecustomize.py'],
            env=env,
        )
        assert out.startswith(b'Test success')

    def test_sitecustomize_run_suppressed(self):
        # ensure `sitecustomize.py` is not loaded if `-S` is used
        env = inject_sitecustomize('tests/commands/bootstrap')
        out = subprocess.check_output(
            ['oteltrace-run', 'python', '-S', 'tests/commands/oteltrace_run_sitecustomize.py', '-S'],
            env=env,
        )
        assert out.startswith(b'Test success')

    def test_argv_passed(self):
        out = subprocess.check_output(
            ['oteltrace-run', 'python', 'tests/commands/oteltrace_run_argv.py', 'foo', 'bar']
        )
        assert out.startswith(b'Test success')

    def test_global_trace_tags(self):
        """ Ensure global tags are passed in from environment
        """
        with self.override_env(dict(OTEL_TRACE_GLOBAL_TAGS='a:True,b:0,c:C')):
            out = subprocess.check_output(
                ['oteltrace-run', 'python', 'tests/commands/oteltrace_run_global_tags.py']
            )
            assert out.startswith(b'Test success')

    def test_logs_injection(self):
        """ Ensure logs injection works
        """
        with self.override_env(dict(OTEL_LOGS_INJECTION='true')):
            out = subprocess.check_output(
                ['oteltrace-run', 'python', 'tests/commands/oteltrace_run_logs_injection.py']
            )
            assert out.startswith(b'Test success')

    def test_otel_exporter(self):
        """ Ensure exporter is properly loaded
        """
        oteltrace_run_conf = {
            'OTEL_EXPORTER_MODULE': 'tests.commands.module_mock',
            'OTEL_EXPORTER_FACTORY': 'build_exporter',
            'OTEL_EXPORTER_OPTIONS_key': '0x9812892467541',
            'OTEL_EXPORTER_OPTIONS_url': 'opentelemetry.io',
        }
        with self.override_env(oteltrace_run_conf):
            out = subprocess.check_output(
                ['oteltrace-run', 'python', 'tests/commands/oteltrace_run_otelexporter.py']
            )
            assert out.startswith(b'Test success')

    def test_propagator(self):
        """ Ensure correct propagator is configured
        """
        oteltrace_run_conf = {
            'OTEL_TRACER_PROPAGATOR': 'b3',
        }
        with self.override_env(oteltrace_run_conf):
            out = subprocess.check_output(
                ['oteltrace-run', 'python', 'tests/commands/oteltrace_run_propagator.py']
            )
            assert out.startswith(b'Test success')
