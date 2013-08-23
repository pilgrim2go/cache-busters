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

import pretend

from pymysqlreplication.constants import (
    UPDATE_ROWS_EVENT_V1, UPDATE_ROWS_EVENT_V2
)

from twisted.internet.defer import Deferred
from twisted.trial.unittest import TestCase

from cache_buster.databases import MySQLDatabaseListener
from cache_buster.test.doubles import FakeReactor


class MySQLDatabaseListenerTests(TestCase):
    def create_event(self, event_type, table, rows):
        return pretend.stub(
            event_type=event_type,
            table=table,
            rows=rows,
        )

    def test_calls_invalidate_row_on_update_row_v1(self):
        connection = pretend.stub(
            fetchone=lambda: self.create_event(
                UPDATE_ROWS_EVENT_V1, "my_table", [{"before_values": {}}]
            )
        )
        d = Deferred()
        driver = pretend.stub(
            invalidate_row=pretend.call_recorder(lambda table, row: d)
        )
        listener = MySQLDatabaseListener(FakeReactor(), connection, driver)
        iterable = iter(listener)
        next(iterable)
        self.assertEqual(driver.invalidate_row.calls, [
            pretend.call("my_table", {}),
        ])

    def test_calls_invalidate_row_on_update_row_v2(self):
        connection = pretend.stub(
            fetchone=lambda: self.create_event(
                UPDATE_ROWS_EVENT_V2, "my_table", [{"before_values": {}}]
            )
        )
        d = Deferred()
        driver = pretend.stub(
            invalidate_row=pretend.call_recorder(lambda table, row: d)
        )
        listener = MySQLDatabaseListener(FakeReactor(), connection, driver)
        iterable = iter(listener)
        next(iterable)
        self.assertEqual(driver.invalidate_row.calls, [
            pretend.call("my_table", {}),
        ])

    def test_ignores_unknown_event_types(self):
        connection = pretend.stub(
            fetchone=lambda: self.create_event(None, None, None)
        )
        listener = MySQLDatabaseListener(FakeReactor(), connection, None)
        iterable = iter(listener)
        next(iterable)

    def test_calls_invalidate_row_multiple_times_on_update_row(self):
        connection = pretend.stub(
            fetchone=lambda: self.create_event(
                UPDATE_ROWS_EVENT_V2, "my_table", [
                    {"before_values": {}},
                    {"before_values": {}},
                ]
            )
        )
        driver = pretend.stub(
            invalidate_row=pretend.call_recorder(lambda table, row: None)
        )
        listener = MySQLDatabaseListener(FakeReactor(), connection, driver)
        iterable = iter(listener)
        next(iterable)
        self.assertEqual(driver.invalidate_row.calls, [
            pretend.call("my_table", {}),
            pretend.call("my_table", {}),
        ])
