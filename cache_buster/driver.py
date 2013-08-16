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

class Driver(object):
    """
    :attr _fkt: A FormattingKeyThingy.
    :attr _cache: A CacheDeleter.
    """

    def __init__(self, fkt, cache):
        self._fkt = fkt
        self._cache = cache

    def invalidate_row(self, table, row):
        for key in self._fkt.keys_for_row(table, row):
            self._cache.delete(key)
