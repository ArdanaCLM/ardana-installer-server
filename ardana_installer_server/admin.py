# (c) Copyright 2018 SUSE LLC
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

from flask import Blueprint
from flask import jsonify
from flask import request
from oslo_config import cfg
import threading
import time
from util import ping

bp = Blueprint('admin', __name__)
CONF = cfg.CONF
SUCCESS = {"success": True}


def update_trigger_file():
    with open(CONF.general.restart_trigger_file, 'w') as f:
        f.write("Triggered restart at %s\n" % time.asctime())


@bp.route("/api/v1/restart", methods=['POST'])
def restart():
    """Requests the service to restart after a specified delay, in seconds

    .. :quickref: Admin; Requests a service restart after a delay

    **Example Request**:

    .. sourcecode:: http

       POST /api/v2/user HTTP/1.1

       Content-Type: application/json

       {
          "delay": 60
       }
    """
    info = request.get_json() or {}
    delay_secs = int(info.get('delay', 0))

    t = threading.Timer(delay_secs, update_trigger_file)
    t.start()

    return jsonify(SUCCESS)


@bp.route("/api/v1/connection_test", methods=['POST'])
def connection_test():
    body = request.get_json() or {}
    host = body['host']
    try:
        ping(host, 22)
        return jsonify('Success')
    except Exception as e:
        return jsonify(error=str(e)), 404
