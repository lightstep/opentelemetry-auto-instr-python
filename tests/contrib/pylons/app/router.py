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

import os

from routes import Mapper


def create_routes():
    """Change this function if you need to add more routes
    to your Pylons test app.
    """
    app_dir = os.path.dirname(os.path.abspath(__file__))
    controller_dir = os.path.join(app_dir, 'controllers')
    routes = Mapper(directory=controller_dir)
    routes.connect('/', controller='root', action='index')
    routes.connect('/raise_exception', controller='root', action='raise_exception')
    routes.connect('/raise_wrong_code', controller='root', action='raise_wrong_code')
    routes.connect('/raise_custom_code', controller='root', action='raise_custom_code')
    routes.connect('/raise_code_method', controller='root', action='raise_code_method')
    routes.connect('/render', controller='root', action='render')
    routes.connect('/render_exception', controller='root', action='render_exception')
    return routes
