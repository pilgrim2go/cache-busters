"""
Copyright 2013 Rackspace

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
from pymysqlreplication import BinLogStreamReader

from twisted.internet.endpoints import TCP4ClientEndpoint
from twisted.protocols.memcache import DEFAULT_PORT
from twisted.python import usage

import yaml

from cache_buster.caches import MemcachedCache, MultiCache
from cache_buster.databases import (
    DatabaseListenerService, MySQLDatabaseListener
)
from cache_buster.driver import Driver
from cache_buster.keys import FormattingKeyMaker



class Options(usage.Options):
    optParameters = [
        ["config", "c", None, "Path to YAML config file."]
    ]


def makeService(options):
    from twisted.internet import task as cooperator
    from twisted.internet import reactor
    from twisted.python import log

    with open(options['config']) as f:
        data = f.read()
        config = yaml.safe_load(data)
        key_maker = FormattingKeyMaker.from_yaml(data)

    cache_backend = MultiCache([
        MemcachedCache(TCP4ClientEndpoint(reactor, cache, DEFAULT_PORT))
        for cache in config['caches']
    ])

    driver = Driver(key_maker, cache_backend, log)

    connection = BinLogStreamReader(connection_settings=config['database'])

    listener = MySQLDatabaseListener(reactor, connection, driver, log)

    return DatabaseListenerService(cooperator, listener, log)
