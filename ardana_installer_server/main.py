# (c) Copyright 2017-2018 SUSE LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from flask import Flask
from flask_cors import CORS
import os
from oslo_config import cfg
from oslo_log import log as logging
import time

from ardana_installer_server import admin
from ardana_installer_server import ardana
from ardana_installer_server import config  # noqa: F401
from ardana_installer_server import oneview
from ardana_installer_server import socket_proxy
from ardana_installer_server import socketio
from ardana_installer_server import suse_manager
from ardana_installer_server import ui
from ardana_installer_server.util import CustomJSONEncoder

LOG = logging.getLogger(__name__)
CONF = cfg.CONF
logging.register_options(CONF)

# Load config options from config file or command line
CONF()

# Setup the logging per the config options
logging.setup(CONF, 'ardana_installer_service')

app = Flask(__name__,
            static_url_path='',
            static_folder=CONF.general.ui_home)
app.register_blueprint(admin.bp)
app.register_blueprint(ardana.bp)
app.register_blueprint(ui.bp)
app.register_blueprint(oneview.bp)
app.register_blueprint(suse_manager.bp)
app.register_blueprint(socket_proxy.bp)
app.json_encoder = CustomJSONEncoder
# Flask logging is broken, and it is a time bomb: by default it does nothing,
# but the first time an exception happens, it creates a new logger that
# interferes with normal python logging, which messes up all subsequent log
# messages.  This bug was reported in
# https://github.com/pallets/flask/issues/641 and is expected to be fixed in
# the future when Flask 1.0 ships.  Referring to app.logger forces this
# creation via Flask's logger property handler.  We then clean up the mess it
# makes
app.logger                   # initialize flask logging (screwing up logging)
app.logger.handlers = []     # clear out the newly creating logger
app.logger.propagate = True  # let messages be handled by normal logging

CORS(app)


@app.route('/')
def root():
    return app.send_static_file('index.html')


def main():

    socketio.init_app(app)

    trigger_file = 'uiservertrigger.txt'
    with open(trigger_file, 'w') as f:
        f.write("Started at %s\n" % time.asctime())

    # The 'log' parameter avoids running in debug mode, which suppresses the
    # debug message that is emitted on *every* incoming request.
    socketio.run(app,
                 host=CONF.general.host,
                 port=CONF.general.port,
                 log=LOG,
                 use_reloader=True,
                 extra_files=[trigger_file])

if __name__ == "__main__":
    main()
