cache_busters
=============

``cache_busters`` is an automatic cache invalidation system. It works by
listening on a database's (such as PostgreSQL or MySQL) replication protocol,
and invalidating caches (such as memcached or redis) based on dirtied data.

Basic architecture:

* Can be configured via either a simple configuration file (for individual
  deployments) or via a REST API (for multi-tenanted deployments).
* A coordinator is responsible for making sure that at all times there is a
  live ``cache_busters`` node which is handling invalidation for a given
  database. It's ok if there are multiple running.
* In a multi-tenanted deployment, configuration data is stored in a database.
* Inside each ``cache_busters`` node, connections to a cache are stored in a
  variable sized pool and invalidated by LRU.
* It never tries to repopulate a cache, only flush.
* An example configuration file (need to figure out the REST equivalent)::

  caches:
    - "127.0.0.1"

  database:
    host: "127.0.0.1"
    user: "root"

  on_update:
    test_table:
      - "{id}-{name}"
    animals:
      - "{id}-{name}"

TODO
----

* Figure out what sort of cooperation we need to pretend to be a slave.
* In multi-tenanted mode how does the networking for all this work out.
