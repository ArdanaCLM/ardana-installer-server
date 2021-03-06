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
from . import socketio
import eventlet
from flask import Blueprint
from flask import copy_current_request_context
from flask import request
from flask_socketio import emit
from oslo_config import cfg
from oslo_log import log as logging
from socketIO_client import BaseNamespace
from socketIO_client import SocketIO
import sys

if sys.version_info.major < 3:
    from urlparse import urlparse
else:
    from urllib.parse import urlparse

CONF = cfg.CONF
LOG = logging.getLogger(__name__)

bp = Blueprint('socket_proxy', __name__)


LOG_NAMESPACE = '/log'
EVENT_NAMESPACE = '/event'


class SocketProxy(object):
    def __init__(self, id, host, port):
        self.client = SocketIO(host, port, BaseNamespace)
        self.client.on('log', self.on_log)
        self.client.on('end', self.on_end)
        self.client.on('playbook-start', self.on_playbook_start)
        self.client.on('playbook-stop', self.on_playbook_stop)
        self.client.on('playbook-error', self.on_playbook_error)
        self.client.emit('join', id)

    def on_log(self, message):
        emit("log", message)

    def on_end(self, message):
        emit("end")
        self.client.disconnect()

    def on_playbook_start(self, playbook):
        emit("playbook-start", playbook)

    def on_playbook_stop(self, playbook):
        emit("playbook-stop", playbook)

    def on_playbook_error(self, playbook):
        emit("playbook-error", playbook)

    def wait(self):
        self.client.wait()  # seconds=5)
        # Hack! _close is needed to *really* close the connection
        self.client._close()


@socketio.on('join')
def on_join(id):
    LOG.debug("Received request by %s to join %s", request.sid, id)

    @copy_current_request_context
    def wait_for_messages(id):

        # Per the socketIO-client documentation, the hostname parameter
        # must be prefixed with https:// in order to use SSL.
        url = urlparse(CONF.general.ardana_service_url)
        if url.scheme == 'https':
            host = 'https://' + url.hostname
        else:
            host = url.hostname

        proxy = SocketProxy(id, host, url.port)
        proxy.wait()

    eventlet.spawn(wait_for_messages, id)
