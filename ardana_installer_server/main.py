# (c) Copyright 2017 SUSE LLC
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
import logging
from oslo_config import cfg

from ardana_installer_server import ardana
from ardana_installer_server import config  # noqa: F401
from ardana_installer_server import oneview
from ardana_installer_server import socket_proxy
from ardana_installer_server import socketio
from ardana_installer_server import suse_manager
from ardana_installer_server import ui


# attempt to set the log file to /var/log/cloudinstaller/install.log, but if
# it's not writable, still configure default logging level to DEBUG
try:
    logging.basicConfig(level=logging.DEBUG,
                        filename='/var/log/cloudinstaller/install.log')
except IOError:
    logging.basicConfig(level=logging.DEBUG)

LOG = logging.getLogger(__name__)

CONF = cfg.CONF
# Load config options from config file or command line
CONF()

app = Flask(__name__,
            static_url_path='',
            static_folder=CONF.general.ui_home)
app.register_blueprint(ardana.bp)
app.register_blueprint(ui.bp)
app.register_blueprint(oneview.bp)
app.register_blueprint(suse_manager.bp)
app.register_blueprint(socket_proxy.bp)
CORS(app)


@app.route('/')
def root():
    return app.send_static_file('index.html')


if __name__ == "__main__":

    socketio.init_app(app)
    socketio.run(app,
                 host=CONF.general.host,
                 port=CONF.general.port,
                 use_reloader=True)
