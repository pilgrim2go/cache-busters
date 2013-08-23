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

from pymysqlreplication.constants import (
    UPDATE_ROWS_EVENT_V1, UPDATE_ROWS_EVENT_V2
)

from twisted.application.service import Service


class DatabaseListenerService(Service):
    def __init__(self, cooperator, listener, log):
        self._listener = listener
        self._cooperator = cooperator
        self._log = log
        self._task = None

    def startService(self):
        self._task = self._cooperator.cooperate(iter(self._listener))
        self._task.whenDone().addErrback(self._log.err)

    def stopService(self):
        return self._task.stop()


class MySQLDatabaseListener(object):
    def __init__(self, reactor, connection, driver, logger):
        super(MySQLDatabaseListener, self).__init__()
        self._reactor = reactor
        self._connection = connection
        self._driver = driver
        self._logger = logger

    def __iter__(self):
        while True:
            event = self._connection.fetchone()
            if (event.event_type == UPDATE_ROWS_EVENT_V1 or
                event.event_type == UPDATE_ROWS_EVENT_V2):
                self._logger.msg("cache_buster.databases.mysql.update",
                    num_rows=len(event.rows)
                )
                for row in event.rows:
                    yield self._driver.invalidate_row(
                        event.table, row["before_values"]
                    )
            else:
                yield
