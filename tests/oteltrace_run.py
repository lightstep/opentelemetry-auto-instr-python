import os
import sys

# DEV: We must append to sys path before importing oteltrace_run
sys.path.append('.')
from oteltrace.commands import oteltrace_run  # noqa

os.environ['PYTHONPATH'] = '{}:{}'.format(os.getenv('PYTHONPATH'), os.path.abspath('.'))
oteltrace_run.main()
