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
from flask import abort
from flask import Blueprint
from flask import jsonify
from flask import request
import socket
import ssl
import xmlrpclib

bp = Blueprint('suse-manager', __name__)

TIMEOUT = 2

"""
Calls to SUSE Manager
"""


def get_client(url, verify_ssl):
    context = ssl._create_default_https_context()
    if verify_ssl == 'false':
        context = ssl._create_unverified_context()

    client = xmlrpclib.Server(url, verbose=0, context=context)
    return client


@bp.route("/api/v1/sm/connection_test", methods=['POST'])
def connection_test():
    context = ssl._create_default_https_context()

    verify_ssl = request.headers.get('Secured')
    if verify_ssl == 'false':
        context = ssl._create_unverified_context()

    creds = request.get_json() or {}
    port = "443"
    if creds['port'] and creds['port'] != 0:
        port = creds['port']
    # check the host and port first before login
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(TIMEOUT)
        s.connect((creds['host'], int(port)))
    except Exception as e:
        return jsonify(error=str(e)), 404

    # login
    try:
        suma_url = "https://" + creds['host'] + ":" + str(port) + "/rpc/api"
        suma_username = creds['username']
        suma_password = creds['password']
        client = xmlrpclib.Server(suma_url, verbose=0, context=context)
        key = client.auth.login(suma_username, suma_password)
        return jsonify(key)
    except Exception as e:
        if 'SSL:' in str(e) or 'doesn\'t match' in str(e):
            return jsonify(error=str(e)), 403
        else:
            return jsonify(error=str(e)), 401


@bp.route("/api/v1/sm/servers")
def sm_server_list():
    try:
        key = request.headers.get('Auth-Token')
        url = request.headers.get('Suse-Manager-Url')
        verify_ssl = request.headers.get('Secured')

        client = get_client(url, verify_ssl)
        server_list = client.system.listActiveSystems(key)

        return jsonify(server_list)
    except Exception as e:
        return jsonify(error=str(e)), 400


@bp.route("/api/v1/sm/servers/<id>")
def sm_server_details(id):
    try:
        key = request.headers.get('Auth-Token')
        url = request.headers.get('Suse-Manager-Url')
        verify_ssl = request.headers.get('Secured')

        client = get_client(url, verify_ssl)
        detail_list = client.system.listActiveSystemsDetails(key, int(id))

        detail = detail_list[0].copy()
        detail.update(client.system.getDetails(key, int(id)))


        return jsonify(detail)
    except Exception as e:
        return jsonify(error=str(e)), 400
