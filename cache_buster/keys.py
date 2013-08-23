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

import yaml


class FormattingKeyMaker(object):
    """
    :attribute dict _table_formats: Mapping of table names to a list of key
        formats.
    """

    @classmethod
    def from_yaml(cls, ini_string):
        return cls(yaml.safe_load(ini_string)["invalidations"])

    def __init__(self, table_formats):
        self._table_formats = table_formats

    def keys_for_row(self, table, row):
        for format in self._table_formats.get(table, []):
            try:
                yield format.format(**row)
            except KeyError:
                # TODO: Do not ignore this exception, at a minimum it should be
                # logged
                pass
