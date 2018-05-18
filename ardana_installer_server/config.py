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
from oslo_config import cfg

general_opts = [
    cfg.IPOpt('host',
              default='0.0.0.0',
              help='IP address to listen on.'),
    cfg.PortOpt('port',
                default=3000,
                help='Port number to listen on.'),
    cfg.StrOpt('db_file',
               default='/tmp/db.json',
               help='Location of database for discovered servers'),
    cfg.StrOpt('progress_file',
               default='/tmp/progress.json',
               help='Location of file to track progress through UI'),
    cfg.StrOpt('restart_trigger_file',
               default='/tmp/cloud_install_ui_trigger.txt',
               help='Location of file to trigger a flask restart to pickup new configs'),
    cfg.StrOpt('ui_home',
               default='web',
               help='Location of static files to serve'),
    cfg.URIOpt('ardana_service_url',
               default='http://localhost:9085',
               help='URL of ardana service'),
]

url_opts = [
    cfg.StrOpt('horizon',
               help='Location of horizon UI'),
    cfg.StrOpt('opsconsole',
               help='Location of operations console UI'),
]

url_group = cfg.OptGroup(name='urls',
                         title='URLs to be displayed on the completion page')

CONF = cfg.CONF
CONF.register_opts(general_opts, 'general')
CONF.register_group(url_group)
CONF.register_opts(url_opts, url_group)


# This function is used by "tox -e genopts" to generate a config file
# containing all options
def list_opts():
    return [('general', general_opts), ('urls', url_opts)]
