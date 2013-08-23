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


class MySQLDatabaseListener(object):
    def __init__(self, reactor, connection, driver):
        super(MySQLDatabaseListener, self).__init__()
        self._reactor = reactor
        self._connection = connection
        self._driver = driver

    def __iter__(self):
        while True:
            event = self._connection.fetchone()
            if (event.event_type == UPDATE_ROWS_EVENT_V1 or
                event.event_type == UPDATE_ROWS_EVENT_V2):
                for row in event.rows:
                    yield self._driver.invalidate_row(
                        event.table, row["before_values"]
                    )
            else:
                yield
