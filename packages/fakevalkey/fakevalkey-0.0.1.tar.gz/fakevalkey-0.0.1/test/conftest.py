from typing import Callable, Tuple, Union, Optional

import pytest
import pytest_asyncio
import valkey

import fakevalkey
from fakevalkey._server import _create_version


def _check_lua_module_supported() -> bool:
    valkey = fakevalkey.FakeValkey(lua_modules={"cjson"})
    try:
        valkey.eval("return cjson.encode({})", 0)
        return True
    except Exception:
        return False


@pytest_asyncio.fixture(scope="session")
def real_redis_version() -> Tuple[str, Union[None, Tuple[int, ...]]]:
    """Returns server's version or None if server is not running"""
    client = None
    try:
        client = valkey.StrictValkey("localhost", port=6380, db=2)
        client_info = client.info()
        server_type = "dragonfly" if "dragonfly_version" in client_info else "valkey"
        server_version = client_info["redis_version"] if server_type != "dragonfly" else (7, 0)
        server_version = _create_version(server_version) or (7,)
        return server_type, server_version
    except valkey.ConnectionError as e:
        pytest.exit("Redis is not running")
        return "valkey", (6,)
    finally:
        if hasattr(client, "close"):
            client.close()  # Absent in older versions of valkey-py


@pytest_asyncio.fixture(name="fake_server")
def _fake_server(request) -> fakevalkey.FakeServer:
    min_server_marker = request.node.get_closest_marker("min_server")
    server_version = min_server_marker.args[0] if min_server_marker else "6.2"
    server = fakevalkey.FakeServer(version=server_version)
    server.connected = request.node.get_closest_marker("disconnected") is None
    return server


@pytest_asyncio.fixture
def r(request, create_redis) -> valkey.Valkey:
    rconn = create_redis(db=2)
    connected = request.node.get_closest_marker("disconnected") is None
    if connected:
        rconn.flushall()
    yield rconn
    if connected:
        rconn.flushall()
    if hasattr(r, "close"):
        rconn.close()  # Older versions of valkey-py don't have this method


def _marker_version_value(request, marker_name: str):
    marker_value = request.node.get_closest_marker(marker_name)
    if marker_value is None:
        return (0,) if marker_name == "min_server" else (100,)
    return _create_version(marker_value.args[0])


@pytest_asyncio.fixture(
    name="create_redis",
    params=[
        pytest.param("StrictValkey", marks=pytest.mark.real),
        pytest.param("FakeStrictValkey", marks=pytest.mark.fake),
    ],
)
def _create_redis(request) -> Callable[[int], valkey.Valkey]:
    cls_name = request.param
    server_type, server_version = request.getfixturevalue("real_redis_version")
    if not cls_name.startswith("Fake") and not server_version:
        pytest.skip("Redis is not running")
    unsupported_server_types = request.node.get_closest_marker("unsupported_server_types")
    if unsupported_server_types and server_type in unsupported_server_types.args:
        pytest.skip(f"Server type {server_type} is not supported")
    min_server = _marker_version_value(request, "min_server")
    max_server = _marker_version_value(request, "max_server")
    if server_version < min_server:
        pytest.skip(f"Redis server {min_server} or more required but {server_version} found")
    if server_version > max_server:
        pytest.skip(f"Redis server {max_server} or less required but {server_version} found")
    decode_responses = request.node.get_closest_marker("decode_responses") is not None
    lua_modules_marker = request.node.get_closest_marker("load_lua_modules")
    lua_modules = set(lua_modules_marker.args) if lua_modules_marker else None
    if lua_modules and not _check_lua_module_supported():
        pytest.skip("LUA modules not supported by fakevalkey")

    def factory(db=2):
        if cls_name.startswith("Fake"):
            fake_server = request.getfixturevalue("fake_server")
            cls = getattr(fakevalkey, cls_name)
            return cls(db=db, decode_responses=decode_responses, server=fake_server, lua_modules=lua_modules)
        # Real
        cls = getattr(valkey, cls_name)
        return cls("localhost", port=6380, db=db, decode_responses=decode_responses)

    return factory


@pytest_asyncio.fixture(
    name="async_redis",
    params=[pytest.param("fake", marks=pytest.mark.fake), pytest.param("real", marks=pytest.mark.real)],
)
async def _req_aioredis2(request) -> valkey.asyncio.Valkey:
    server_type, server_version = request.getfixturevalue("real_redis_version")
    if request.param != "fake" and not server_version:
        pytest.skip("Redis is not running")
    unsupported_server_types = request.node.get_closest_marker("unsupported_server_types")
    if unsupported_server_types and server_type in unsupported_server_types.args:
        pytest.skip(f"Server type {server_type} is not supported")
    min_server_marker = _marker_version_value(request, "min_server")
    max_server_marker = _marker_version_value(request, "max_server")
    if server_version < min_server_marker:
        pytest.skip(f"Redis server {min_server_marker} or more required but {server_version} found")
    if server_version > max_server_marker:
        pytest.skip(f"Redis server {max_server_marker} or less required but {server_version} found")
    lua_modules_marker = request.node.get_closest_marker("load_lua_modules")
    lua_modules = set(lua_modules_marker.args) if lua_modules_marker else None
    if lua_modules and not _check_lua_module_supported():
        pytest.skip("LUA modules not supported by fakevalkey")
    fake_server: Optional[fakevalkey.FakeServer]
    if request.param == "fake":
        fake_server = request.getfixturevalue("fake_server")
        ret = fakevalkey.FakeAsyncRedis(server=fake_server, lua_modules=lua_modules)
    else:
        ret = valkey.asyncio.Valkey(host="localhost", port=6380, db=2)
        fake_server = None
    if not fake_server or fake_server.connected:
        await ret.flushall()

    yield ret

    if not fake_server or fake_server.connected:
        await ret.flushall()
    await ret.connection_pool.disconnect()
