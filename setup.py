import copy
import os
import sys

from distutils.command.build_ext import build_ext
from distutils.errors import CCompilerError, DistutilsExecError, DistutilsPlatformError
from setuptools import setup, find_packages, Extension
from setuptools.command.test import test as TestCommand


class Tox(TestCommand):

    user_options = [('tox-args=', 'a', 'Arguments to pass to tox')]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.tox_args = None

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        # import here, cause outside the eggs aren't loaded
        import tox
        import shlex
        args = self.tox_args
        if args:
            args = shlex.split(self.tox_args)
        errno = tox.cmdline(args=args)
        sys.exit(errno)


long_description = """
# otel-trace-py

`oteltrace` is OpenTelemetry's tracing library for Python.  It is used to trace requests
as they flow across web servers, databases and microservices so that developers
have great visiblity into bottlenecks and troublesome requests.

## Getting Started

For a basic product overview, installation and quick start, check out our
[setup documentation][setup docs].

For more advanced usage and configuration, check out our [API
documentation][pypi docs].

For descriptions of terminology used in APM, take a look at the [official
documentation][visualization docs].

[setup docs]: https://docs.datadoghq.com/tracing/setup/python/
[pypi docs]: http://pypi.datadoghq.com/trace/docs/
[visualization docs]: https://docs.datadoghq.com/tracing/visualization/
"""

# Base `setup()` kwargs without any C-extension registering
setup_kwargs = dict(
    name='oteltrace',
    description='OpenTelemetry tracing code',
    url='https://github.com/opentelemetry/otel-trace-py',
    author='DataDog, Inc.',
    author_email='dev@datadoghq.com',
    long_description=long_description,
    long_description_content_type='text/markdown',
    license='BSD',
    packages=find_packages(exclude=['tests*']),
    install_requires=[
        'psutil>=5.0.0',
        'opentelemetry-api',
        'opentelemetry-sdk',
    ],
    # plugin tox
    tests_require=['tox', 'flake8'],
    cmdclass={'test': Tox},
    entry_points={
        'console_scripts': [
            'oteltrace-run = oteltrace.commands.oteltrace_run:main'
        ]
    },
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    use_scm_version=True,
    setup_requires=['setuptools_scm', 'opentelemetry-api', 'opentelemetry-sdk'],
)


libraries = []
if sys.platform == 'win32':
    libraries.append('ws2_32')
    build_ext_errors = (CCompilerError, DistutilsExecError, DistutilsPlatformError, IOError, OSError)
else:
    build_ext_errors = (CCompilerError, DistutilsExecError, DistutilsPlatformError)


class BuildExtFailed(Exception):
    pass


# Attempt to build a C-extension, catch and throw a common/custom error if there are any issues
class optional_build_ext(build_ext):
    def run(self):
        try:
            build_ext.run(self)
        except DistutilsPlatformError:
            raise BuildExtFailed()

    def build_extension(self, ext):
        try:
            build_ext.build_extension(self, ext)
        except build_ext_errors:
            raise BuildExtFailed()


macros = []
if sys.byteorder == 'big':
    macros = [('__BIG_ENDIAN__', '1')]
else:
    macros = [('__LITTLE_ENDIAN__', '1')]


# Try to build with C extensions first, fallback to only pure-Python if building fails
try:
    kwargs = copy.deepcopy(setup_kwargs)
    kwargs['ext_modules'] = [
        Extension(
            'oteltrace.vendor.wrapt._wrappers',
            sources=['oteltrace/vendor/wrapt/_wrappers.c'],
        ),
    ]
    # DEV: Make sure `cmdclass` exists
    kwargs.setdefault('cmdclass', dict())
    kwargs['cmdclass']['build_ext'] = optional_build_ext
    setup(**kwargs)
except BuildExtFailed:
    # Set `DDTRACE_BUILD_TRACE=TRUE` in CI to raise any build errors
    if os.environ.get('DDTRACE_BUILD_RAISE') == 'TRUE':
        raise

    print('WARNING: Failed to install wrapt/msgpack C-extensions, using pure-Python wrapt/msgpack instead')
    setup(**setup_kwargs)
