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

from os import getenv

# Celery Context key
CTX_KEY = '__otel_task_span'

# Span names
PRODUCER_ROOT_SPAN = 'celery.apply'
WORKER_ROOT_SPAN = 'celery.run'

# Task operations
TASK_TAG_KEY = 'celery.action'
TASK_APPLY = 'apply'
TASK_APPLY_ASYNC = 'apply_async'
TASK_RUN = 'run'
TASK_RETRY_REASON_KEY = 'celery.retry.reason'

# Service info
APP = 'celery'
# `getenv()` call must be kept for backward compatibility; we may remove it
# later when we do a full migration to the `Config` class
PRODUCER_SERVICE = getenv('OPENTELEMETRY_SERVICE_NAME') or 'celery-producer'
WORKER_SERVICE = getenv('OPENTELEMETRY_SERVICE_NAME') or 'celery-worker'
