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

import sys


if __name__ == '__main__':
    # detect if `-S` is used
    suppress = len(sys.argv) == 2 and sys.argv[1] == '-S'
    if suppress:
        assert 'sitecustomize' not in sys.modules
    else:
        assert 'sitecustomize' in sys.modules

    # ensure the right `sitecustomize` will be imported
    import sitecustomize
    assert sitecustomize.CORRECT_IMPORT
    print('Test success')
