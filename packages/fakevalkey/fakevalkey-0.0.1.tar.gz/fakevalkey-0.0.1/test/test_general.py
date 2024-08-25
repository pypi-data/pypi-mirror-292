import pytest
import valkey

from test.testtools import raw_command


def test_asyncioio_is_used():
    """Redis 4.2+ has support for asyncio and should be preferred over aioredis"""
    from fakevalkey import aioredis

    assert not hasattr(aioredis, "__version__")


def test_unknown_command(r: valkey.Redis):
    with pytest.raises(valkey.ResponseError):
        raw_command(r, "0 3 3")
