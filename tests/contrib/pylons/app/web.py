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

from mako.lookup import TemplateLookup

from pylons import config
from pylons.wsgiapp import PylonsApp

from routes.middleware import RoutesMiddleware
from beaker.middleware import SessionMiddleware, CacheMiddleware

from paste.registry import RegistryManager

from .router import create_routes
from .lib.helpers import AppGlobals


def make_app(global_conf, full_stack=True, **app_conf):
    # load Pylons environment
    root = os.path.dirname(os.path.abspath(__file__))
    paths = dict(
        templates=[os.path.join(root, 'templates')],
    )
    config.init_app(global_conf, app_conf, paths=paths)
    config['pylons.package'] = 'tests.contrib.pylons.app'
    config['pylons.app_globals'] = AppGlobals()

    # set Pylons routes
    config['routes.map'] = create_routes()

    # Create the Mako TemplateLookup, with the default auto-escaping
    config['pylons.app_globals'].mako_lookup = TemplateLookup(
        directories=paths['templates'],
    )

    # define a default middleware stack
    app = PylonsApp()
    app = RoutesMiddleware(app, config['routes.map'])
    app = SessionMiddleware(app, config)
    app = CacheMiddleware(app, config)
    app = RegistryManager(app)
    return app
