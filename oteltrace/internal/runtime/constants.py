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

GC_COUNT_GEN0 = 'runtime.python.gc.count.gen0'
GC_COUNT_GEN1 = 'runtime.python.gc.count.gen1'
GC_COUNT_GEN2 = 'runtime.python.gc.count.gen2'

THREAD_COUNT = 'runtime.python.thread_count'
MEM_RSS = 'runtime.python.mem.rss'
CPU_TIME_SYS = 'runtime.python.cpu.time.sys'
CPU_TIME_USER = 'runtime.python.cpu.time.user'
CPU_PERCENT = 'runtime.python.cpu.percent'
CTX_SWITCH_VOLUNTARY = 'runtime.python.cpu.ctx_switch.voluntary'
CTX_SWITCH_INVOLUNTARY = 'runtime.python.cpu.ctx_switch.involuntary'

GC_RUNTIME_METRICS = set([
    GC_COUNT_GEN0,
    GC_COUNT_GEN1,
    GC_COUNT_GEN2,
])

PSUTIL_RUNTIME_METRICS = set([
    THREAD_COUNT,
    MEM_RSS,
    CTX_SWITCH_VOLUNTARY,
    CTX_SWITCH_INVOLUNTARY,
    CPU_TIME_SYS,
    CPU_TIME_USER,
    CPU_PERCENT,
])

DEFAULT_RUNTIME_METRICS = GC_RUNTIME_METRICS | PSUTIL_RUNTIME_METRICS

SERVICE = 'service'
ENV = 'env'
LANG_INTERPRETER = 'lang_interpreter'
LANG_VERSION = 'lang_version'
LANG = 'lang'
TRACER_VERSION = 'tracer_version'

TRACER_TAGS = set([
    SERVICE,
    ENV,
])

PLATFORM_TAGS = set([
    LANG_INTERPRETER,
    LANG_VERSION,
    LANG,
    TRACER_VERSION,
])

DEFAULT_RUNTIME_TAGS = TRACER_TAGS | PLATFORM_TAGS
