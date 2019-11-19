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

FILTERS_KEY = 'FILTERS'
SAMPLE_RATE_METRIC_KEY = '_sample_rate'
SAMPLING_PRIORITY_KEY = '_sampling_priority_v1'
ANALYTICS_SAMPLE_RATE_KEY = '_otel1.sr.eausr'
SAMPLING_AGENT_DECISION = '_otel.agent_psr'
SAMPLING_RULE_DECISION = '_otel.rule_psr'
SAMPLING_LIMIT_DECISION = '_otel.limit_psr'
ORIGIN_KEY = '_otel.origin'
HOSTNAME_KEY = '_otel.hostname'
ENV_KEY = 'env'

NUMERIC_TAGS = (ANALYTICS_SAMPLE_RATE_KEY, )

MANUAL_DROP_KEY = 'manual.drop'
MANUAL_KEEP_KEY = 'manual.keep'
