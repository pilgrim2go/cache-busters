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

    [database]
    type = postgresql
    host = 192.168.1.1
    # etc.

    [cache]
    type = memcache
    host = 192.168.1.1
    # etc.

    [table_name]
    col_name =
        key_name:{with_field_interpolation}
        {field}-other-key

TODO
----

* Figure out what sort of cooperation we need to pretend to be a slave.
* In multi-tenanted mode how does the networking for all this work out.
* If the user has a pool of caches, how do we invalidate, ``DELETE`` on all
  servers, or do we try to use their pooling algorithm. (Almost definitely
  ``DELETE`` to all, we can't know how the user is sharding, and they probably
  get it wrong anyways).
* Did we seriously end up with a distributed coordination problem?
* Punt on multi-tenancy and just make it run as an agent on trove boxes?
