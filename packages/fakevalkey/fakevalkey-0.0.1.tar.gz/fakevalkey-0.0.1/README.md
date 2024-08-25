fakevalkey: A fake version of a valkey-py
=======================================

[![badge](https://img.shields.io/pypi/v/fakevalkey)](https://pypi.org/project/fakevalkey/)
[![CI](https://github.com/cunla/fakevalkey-py/actions/workflows/test.yml/badge.svg)](https://github.com/cunla/fakevalkey-py/actions/workflows/test.yml)
[![badge](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/cunla/b756396efb895f0e34558c980f1ca0c7/raw/fakevalkey-py.json)](https://github.com/cunla/fakevalkey-py/actions/workflows/test.yml)
[![badge](https://img.shields.io/pypi/dm/fakevalkey)](https://pypi.org/project/fakevalkey/)
[![badge](https://img.shields.io/pypi/l/fakevalkey)](./LICENSE)
[![Open Source Helpers](https://www.codetriage.com/cunla/fakevalkey-py/badges/users.svg)](https://www.codetriage.com/cunla/fakevalkey-py)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
--------------------


Documentation is hosted in https://fakevalkey.readthedocs.io/

# Intro

FakeValkey is a pure-Python implementation of the Redis key-value store.

It enables running tests requiring redis server without an actual server.

It provides enhanced versions of the redis-py Python bindings for Redis. That provide the following added functionality:
A built-in Redis server that is automatically installed, configured and managed when the Redis bindings are used. A
single server shared by multiple programs or multiple independent servers. All the servers provided by
FakeRedis support all Redis functionality including advanced features such as RedisJson, GeoCommands.

See [official documentation](https://fakevalkey.readthedocs.io/) for list of supported commands.

# Sponsor

fakevalkey-py is developed for free.

You can support this project by becoming a sponsor using [this link](https://github.com/sponsors/cunla).
