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
from flask import abort
from flask.json import JSONEncoder
import datetime
import requests
import socket
import xmlrpclib

TIMEOUT = 2

class CustomJSONEncoder(JSONEncoder):
    def default(self, obj):
        try:
            if isinstance(obj, xmlrpclib.DateTime):
                return datetime.datetime.strptime(
                    obj.value, "%Y%m%dT%H:%M:%S").isoformat()
            iterable = iter(obj)
        except TypeError:
            pass
        else:
            return list(iterable)
        return JSONEncoder.default(self, obj)

# Forward the url to the given destination
def forward(url, request):

    req = requests.Request(method=request.method, url=url, params=request.args,
                           headers=request.headers, data=request.data)

    resp = requests.Session().send(req.prepare())

    return (resp.text, resp.status_code, resp.headers.items())


def ping(host, port):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(TIMEOUT)
        s.connect((host, port))
    except Exception:
        abort(404)
