import pytest

import fakevalkey


def test_multidb(create_redis):
    r1 = create_redis(db=2)
    r2 = create_redis(db=3)

    r1["r1"] = "r1"
    r2["r2"] = "r2"

    assert "r2" not in r1
    assert "r1" not in r2

    assert r1["r1"] == b"r1"
    assert r2["r2"] == b"r2"

    assert r1.flushall() is True

    assert "r1" not in r1
    assert "r2" not in r2


@pytest.mark.fake
class TestInitArgs:
    def test_singleton(self):
        shared_server = fakevalkey.FakeServer()
        r1 = fakevalkey.FakeValkey()
        r2 = fakevalkey.FakeValkey(server=fakevalkey.FakeServer())
        r3 = fakevalkey.FakeValkey(server=shared_server)
        r4 = fakevalkey.FakeValkey(server=shared_server)

        r1.set("foo", "bar")
        r3.set("bar", "baz")

        assert "foo" in r1
        assert "foo" not in r2
        assert "foo" not in r3

        assert "bar" in r3
        assert "bar" in r4
        assert "bar" not in r1

    def test_host_init_arg(self):
        db = fakevalkey.FakeStrictValkey(host="localhost")
        db.set("foo", "bar")
        assert db.get("foo") == b"bar"

    def test_from_url(self):
        db = fakevalkey.FakeStrictValkey.from_url("valkey://localhost:6380/0")
        db.set("foo", "bar")
        assert db.get("foo") == b"bar"

    def test_from_url_user(self):
        db = fakevalkey.FakeStrictValkey.from_url("valkey://user@localhost:6380/0")
        db.set("foo", "bar")
        assert db.get("foo") == b"bar"

    def test_from_url_user_password(self):
        db = fakevalkey.FakeStrictValkey.from_url("valkey://user:password@localhost:6380/0")
        db.set("foo", "bar")
        assert db.get("foo") == b"bar"

    def test_from_url_with_db_arg(self):
        db = fakevalkey.FakeStrictValkey.from_url("valkey://localhost:6380/0")
        db1 = fakevalkey.FakeStrictValkey.from_url("valkey://localhost:6380/1")
        db2 = fakevalkey.FakeStrictValkey.from_url("valkey://localhost:6380/", db=2)
        db.set("foo", "foo0")
        db1.set("foo", "foo1")
        db2.set("foo", "foo2")
        assert db.get("foo") == b"foo0"
        assert db1.get("foo") == b"foo1"
        assert db2.get("foo") == b"foo2"

    def test_from_url_db_value_error(self):
        # In the case of ValueError, should default to 0, or be absent in valkey-py 4.0
        db = fakevalkey.FakeStrictValkey.from_url("valkey://localhost:6380/a")
        assert db.connection_pool.connection_kwargs.get("db", 0) == 0

    def test_can_pass_through_extra_args(self):
        db = fakevalkey.FakeStrictValkey.from_url("valkey://localhost:6380/0", decode_responses=True)
        db.set("foo", "bar")
        assert db.get("foo") == "bar"

    def test_can_allow_extra_args(self):
        db = fakevalkey.FakeStrictValkey.from_url(
            "valkey://localhost:6380/0",
            socket_connect_timeout=11,
            socket_timeout=12,
            socket_keepalive=True,
            socket_keepalive_options={60: 30},
            socket_type=1,
            retry_on_timeout=True,
        )
        fake_conn = db.connection_pool.make_connection()
        assert fake_conn.socket_connect_timeout == 11
        assert fake_conn.socket_timeout == 12
        assert fake_conn.socket_keepalive is True
        assert fake_conn.socket_keepalive_options == {60: 30}
        assert fake_conn.socket_type == 1
        assert fake_conn.retry_on_timeout is True

        # Make fallback logic match valkey-py
        db = fakevalkey.FakeStrictValkey.from_url(
            "valkey://localhost:6380/0", socket_connect_timeout=None, socket_timeout=30
        )
        fake_conn = db.connection_pool.make_connection()
        assert fake_conn.socket_connect_timeout == fake_conn.socket_timeout
        assert fake_conn.socket_keepalive_options == {}

    def test_repr(self):
        # repr is human-readable, so we only test that it doesn't crash,
        # and that it contains the db number.
        db = fakevalkey.FakeStrictValkey.from_url("valkey://localhost:6380/11")
        rep = repr(db)
        assert "db=11" in rep

    def test_from_unix_socket(self):
        db = fakevalkey.FakeStrictValkey.from_url("unix://a/b/c")
        db.set("foo", "bar")
        assert db.get("foo") == b"bar"

    def test_same_connection_params(self):
        r1 = fakevalkey.FakeStrictValkey.from_url("valkey://localhost:6380/11")
        r2 = fakevalkey.FakeStrictValkey.from_url("valkey://localhost:6380/11")
        r3 = fakevalkey.FakeStrictValkey(server=fakevalkey.FakeServer())
        r1.set("foo", "bar")
        assert r2.get("foo") == b"bar"
        assert not r3.exists("foo")

    def test_new_server_with_positional_args(self):
        from fakevalkey import FakeValkey

        # same host, default port and db index
        fake_redis_1 = FakeValkey("localhost")
        fake_redis_2 = FakeValkey("localhost")

        fake_redis_1.set("foo", "bar")

        assert fake_redis_2.get("foo") == b"bar"

        # same host and port
        fake_redis_1 = FakeValkey("localhost", 6000)
        fake_redis_2 = FakeValkey("localhost", 6000)

        fake_redis_1.set("foo", "bar")

        assert fake_redis_2.get("foo") == b"bar"

        # same connection parameters, but different db index
        fake_redis_1 = FakeValkey("localhost", 6000, 0)
        fake_redis_2 = FakeValkey("localhost", 6000, 1)

        fake_redis_1.set("foo", "bar")

        assert fake_redis_2.get("foo") is None

        # mix of positional arguments and keyword args
        fake_redis_1 = FakeValkey("localhost", port=6000, db=0)
        fake_redis_2 = FakeValkey("localhost", port=6000, db=1)

        fake_redis_1.set("foo", "bar")

        assert fake_redis_2.get("foo") is None
