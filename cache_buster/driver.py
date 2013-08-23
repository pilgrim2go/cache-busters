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

from twisted.internet.defer import gatherResults


def count_cache_results(results):
    deletes = nonexistant = failures = 0
    for r in results:
        if r is None:
            failures += 1
        elif r:
            deletes += 1
        else:
            nonexistant += 1
    return deletes, nonexistant, failures


class Driver(object):
    """
    :attr _key_maker: An IKeyMaker.
    :attr _cache: A CacheDeleter.
    :attr _logger: A logger.
    """

    def __init__(self, _key_maker, cache, logger):
        self._key_maker = _key_maker
        self._cache = cache
        self._logger = logger

    def invalidate_row(self, table, row):
        def log_counts(results):
            deletes, nonexistant, failures = count_cache_results(results)
            self._logger.msg("cache_buster.driver.invalidated_rows",
                deletes=deletes, nonexistant=nonexistant, failures=failures
            )

        return gatherResults([
            self._cache.delete(key).addErrback(self._logger.err, table, key)
            for key in self._key_maker.keys_for_row(table, row)
        ]).addCallback(log_counts)
