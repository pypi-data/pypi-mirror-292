from __future__ import annotations

import logging

import pytest
import valkey
import valkey.client
from valkey.exceptions import ResponseError

import fakevalkey
from test import testtools
from test.testtools import raw_command

json_tests = pytest.importorskip("lupa")


@pytest.mark.min_server("7")
def test_script_exists_redis7(r: valkey.Redis):
    # test response for no arguments by bypassing the py-valkey command
    # as it requires at least one argument
    with pytest.raises(valkey.ResponseError):
        raw_command(r, "SCRIPT EXISTS")

    # use single character characters for non-existing scripts, as those
    # will never be equal to an actual sha1 hash digest
    assert r.script_exists("a") == [0]
    assert r.script_exists("a", "b", "c", "d", "e", "f") == [0, 0, 0, 0, 0, 0]

    sha1_one = r.script_load("return 'a'")
    assert r.script_exists(sha1_one) == [1]
    assert r.script_exists(sha1_one, "a") == [1, 0]
    assert r.script_exists("a", "b", "c", sha1_one, "e") == [0, 0, 0, 1, 0]

    sha1_two = r.script_load("return 'b'")
    assert r.script_exists(sha1_one, sha1_two) == [1, 1]
    assert r.script_exists("a", sha1_one, "c", sha1_two, "e", "f") == [0, 1, 0, 1, 0, 0]


@pytest.mark.parametrize("args", [("a",), tuple("abcdefghijklmn")])
def test_script_flush_errors_with_args(r, args):
    with pytest.raises(valkey.ResponseError):
        raw_command(r, "SCRIPT FLUSH %s" % " ".join(args))


def test_script_flush(r: valkey.Redis):
    # generate/load six unique scripts and store their sha1 hash values
    sha1_values = [r.script_load("return '%s'" % char) for char in "abcdef"]

    # assert the scripts all exist prior to flushing
    assert r.script_exists(*sha1_values) == [1] * len(sha1_values)

    # flush and assert OK response
    assert r.script_flush() is True

    # assert none of the scripts exists after flushing
    assert r.script_exists(*sha1_values) == [0] * len(sha1_values)


def test_script_no_subcommands(r: valkey.Redis):
    with pytest.raises(valkey.ResponseError):
        raw_command(r, "SCRIPT")


@pytest.mark.max_server("7")
def test_script_help(r: valkey.Redis):
    assert raw_command(r, "SCRIPT HELP") == [
        b"SCRIPT <subcommand> [<arg> [value] [opt] ...]. Subcommands are:",
        b"DEBUG (YES|SYNC|NO)",
        b"    Set the debug mode for subsequent scripts executed.",
        b"EXISTS <sha1> [<sha1> ...]",
        b"    Return information about the existence of the scripts in the script cach" b"e.",
        b"FLUSH [ASYNC|SYNC]",
        b"    Flush the Lua scripts cache. Very dangerous on replicas.",
        b"    When called without the optional mode argument, the behavior is determin" b"ed by the",
        b"    lazyfree-lazy-user-flush configuration directive. Valid modes are:",
        b"    * ASYNC: Asynchronously flush the scripts cache.",
        b"    * SYNC: Synchronously flush the scripts cache.",
        b"KILL",
        b"    Kill the currently executing Lua script.",
        b"LOAD <script>",
        b"    Load a script into the scripts cache without executing it.",
        b"HELP",
        b"    Prints this help.",
    ]


@pytest.mark.min_server("7.1")
def test_script_help71(r: valkey.Redis):
    assert raw_command(r, "SCRIPT HELP") == [
        b"SCRIPT <subcommand> [<arg> [value] [opt] ...]. Subcommands are:",
        b"DEBUG (YES|SYNC|NO)",
        b"    Set the debug mode for subsequent scripts executed.",
        b"EXISTS <sha1> [<sha1> ...]",
        b"    Return information about the existence of the scripts in the script cach" b"e.",
        b"FLUSH [ASYNC|SYNC]",
        b"    Flush the Lua scripts cache. Very dangerous on replicas.",
        b"    When called without the optional mode argument, the behavior is determin" b"ed by the",
        b"    lazyfree-lazy-user-flush configuration directive. Valid modes are:",
        b"    * ASYNC: Asynchronously flush the scripts cache.",
        b"    * SYNC: Synchronously flush the scripts cache.",
        b"KILL",
        b"    Kill the currently executing Lua script.",
        b"LOAD <script>",
        b"    Load a script into the scripts cache without executing it.",
        b"HELP",
        b"    Print this help.",
    ]


@pytest.mark.max_server("7.1")
def test_eval_blpop(r: valkey.Redis):
    r.rpush("foo", "bar")
    with pytest.raises(valkey.ResponseError, match="This Redis command is not allowed from script"):
        r.eval('return valkey.pcall("BLPOP", KEYS[1], 1)', 1, "foo")


def test_eval_set_value_to_arg(r: valkey.Redis):
    r.eval('valkey.call("SET", KEYS[1], ARGV[1])', 1, "foo", "bar")
    val = r.get("foo")
    assert val == b"bar"


def test_eval_conditional(r: valkey.Redis):
    lua = """
    local val = valkey.call("GET", KEYS[1])
    if val == ARGV[1] then
        valkey.call("SET", KEYS[1], ARGV[2])
    else
        valkey.call("SET", KEYS[1], ARGV[1])
    end
    """
    r.eval(lua, 1, "foo", "bar", "baz")
    val = r.get("foo")
    assert val == b"bar"
    r.eval(lua, 1, "foo", "bar", "baz")
    val = r.get("foo")
    assert val == b"baz"


def test_eval_table(r: valkey.Redis):
    lua = """
    local a = {}
    a[1] = "foo"
    a[2] = "bar"
    a[17] = "baz"
    return a
    """
    val = r.eval(lua, 0)
    assert val == [b"foo", b"bar"]


def test_eval_table_with_nil(r: valkey.Redis):
    lua = """
    local a = {}
    a[1] = "foo"
    a[2] = nil
    a[3] = "bar"
    return a
    """
    val = r.eval(lua, 0)
    assert val == [b"foo"]


def test_eval_table_with_numbers(r: valkey.Redis):
    lua = """
    local a = {}
    a[1] = 42
    return a
    """
    val = r.eval(lua, 0)
    assert val == [42]


def test_eval_nested_table(r: valkey.Redis):
    lua = """
    local a = {}
    a[1] = {}
    a[1][1] = "foo"
    return a
    """
    val = r.eval(lua, 0)
    assert val == [[b"foo"]]


def test_eval_iterate_over_argv(r: valkey.Redis):
    lua = """
    for i, v in ipairs(ARGV) do
    end
    return ARGV
    """
    val = r.eval(lua, 0, "a", "b", "c")
    assert val == [b"a", b"b", b"c"]


def test_eval_iterate_over_keys(r: valkey.Redis):
    lua = """
    for i, v in ipairs(KEYS) do
    end
    return KEYS
    """
    val = r.eval(lua, 2, "a", "b", "c")
    assert val == [b"a", b"b"]


def test_eval_mget(r: valkey.Redis):
    r.set("foo1", "bar1")
    r.set("foo2", "bar2")
    val = r.eval('return valkey.call("mget", "foo1", "foo2")', 2, "foo1", "foo2")
    assert val == [b"bar1", b"bar2"]


def test_eval_mget_not_set(r: valkey.Redis):
    val = r.eval('return valkey.call("mget", "foo1", "foo2")', 2, "foo1", "foo2")
    assert val == [None, None]


def test_eval_hgetall(r: valkey.Redis):
    r.hset("foo", "k1", "bar")
    r.hset("foo", "k2", "baz")
    val = r.eval('return valkey.call("hgetall", "foo")', 1, "foo")
    sorted_val = sorted([val[:2], val[2:]])
    assert sorted_val == [[b"k1", b"bar"], [b"k2", b"baz"]]


def test_eval_hgetall_iterate(r: valkey.Redis):
    r.hset("foo", "k1", "bar")
    r.hset("foo", "k2", "baz")
    lua = """
    local result = valkey.call("hgetall", "foo")
    for i, v in ipairs(result) do
    end
    return result
    """
    val = r.eval(lua, 1, "foo")
    sorted_val = sorted([val[:2], val[2:]])
    assert sorted_val == [[b"k1", b"bar"], [b"k2", b"baz"]]


def test_eval_invalid_command(r: valkey.Redis):
    with pytest.raises(ResponseError):
        r.eval('return valkey.call("FOO")', 0)


def test_eval_syntax_error(r: valkey.Redis):
    with pytest.raises(ResponseError):
        r.eval('return "', 0)


def test_eval_runtime_error(r: valkey.Redis):
    with pytest.raises(ResponseError):
        r.eval('error("CRASH")', 0)


def test_eval_more_keys_than_args(r: valkey.Redis):
    with pytest.raises(ResponseError):
        r.eval("return 1", 42)


def test_eval_numkeys_float_string(r: valkey.Redis):
    with pytest.raises(ResponseError):
        r.eval("return KEYS[1]", "0.7", "foo")


def test_eval_numkeys_integer_string(r: valkey.Redis):
    val = r.eval("return KEYS[1]", "1", "foo")
    assert val == b"foo"


def test_eval_numkeys_negative(r: valkey.Redis):
    with pytest.raises(ResponseError):
        r.eval("return KEYS[1]", -1, "foo")


def test_eval_numkeys_float(r: valkey.Redis):
    with pytest.raises(ResponseError):
        r.eval("return KEYS[1]", 0.7, "foo")


def test_eval_global_variable(r: valkey.Redis):
    # Redis doesn't allow script to define global variables
    with pytest.raises(ResponseError):
        r.eval("a=10", 0)


def test_eval_global_and_return_ok(r: valkey.Redis):
    # Redis doesn't allow script to define global variables
    with pytest.raises(ResponseError):
        r.eval(
            """
            a=10
            return valkey.status_reply("Everything is awesome")
            """,
            0,
        )


def test_eval_convert_number(r: valkey.Redis):
    # Redis forces all Lua numbers to integer
    val = r.eval("return 3.2", 0)
    assert val == 3
    val = r.eval("return 3.8", 0)
    assert val == 3
    val = r.eval("return -3.8", 0)
    assert val == -3


def test_eval_convert_bool(r: valkey.Redis):
    # Redis converts true to 1 and false to nil (which valkey-py converts to None)
    assert r.eval("return false", 0) is None
    val = r.eval("return true", 0)
    assert val == 1
    assert not isinstance(val, bool)


@pytest.mark.min_server("7")
def test_eval_call_bool7(r: valkey.Redis):
    # Redis doesn't allow Lua bools to be passed to [p]call
    with pytest.raises(valkey.ResponseError, match=r"Lua valkey lib command arguments must be strings or integers"):
        r.eval('return valkey.call("SET", KEYS[1], true)', 1, "testkey")


def test_eval_return_error(r: valkey.Redis):
    with pytest.raises(valkey.ResponseError, match="Testing") as exc_info:
        r.eval('return {err="Testing"}', 0)
    assert isinstance(exc_info.value.args[0], str)
    with pytest.raises(valkey.ResponseError, match="Testing") as exc_info:
        r.eval('return valkey.error_reply("Testing")', 0)
    assert isinstance(exc_info.value.args[0], str)


def test_eval_return_redis_error(r: valkey.Redis):
    with pytest.raises(valkey.ResponseError) as exc_info:
        r.eval('return valkey.pcall("BADCOMMAND")', 0)
    assert isinstance(exc_info.value.args[0], str)


def test_eval_return_ok(r: valkey.Redis):
    val = r.eval('return {ok="Testing"}', 0)
    assert val == b"Testing"
    val = r.eval('return valkey.status_reply("Testing")', 0)
    assert val == b"Testing"


def test_eval_return_ok_nested(r: valkey.Redis):
    val = r.eval(
        """
        local a = {}
        a[1] = {ok="Testing"}
        return a
        """,
        0,
    )
    assert val == [b"Testing"]


def test_eval_return_ok_wrong_type(r: valkey.Redis):
    with pytest.raises(valkey.ResponseError):
        r.eval("return valkey.status_reply(123)", 0)


def test_eval_pcall(r: valkey.Redis):
    val = r.eval(
        """
        local a = {}
        a[1] = valkey.pcall("foo")
        return a
        """,
        0,
    )
    assert isinstance(val, list)
    assert len(val) == 1
    assert isinstance(val[0], ResponseError)


def test_eval_pcall_return_value(r: valkey.Redis):
    with pytest.raises(ResponseError):
        r.eval('return valkey.pcall("foo")', 0)


def test_eval_delete(r: valkey.Redis):
    r.set("foo", "bar")
    val = r.get("foo")
    assert val == b"bar"
    val = r.eval('valkey.call("DEL", KEYS[1])', 1, "foo")
    assert val is None


def test_eval_exists(r: valkey.Redis):
    val = r.eval('return valkey.call("exists", KEYS[1]) == 0', 1, "foo")
    assert val == 1


def test_eval_flushdb(r: valkey.Redis):
    r.set("foo", "bar")
    val = r.eval(
        """
        local value = valkey.call("FLUSHDB");
        return type(value) == "table" and value.ok == "OK";
        """,
        0,
    )
    assert val == 1


def test_eval_flushall(r, create_redis):
    r1 = create_redis(db=2)
    r2 = create_redis(db=3)

    r1["r1"] = "r1"
    r2["r2"] = "r2"

    val = r.eval(
        """
        local value = valkey.call("FLUSHALL");
        return type(value) == "table" and value.ok == "OK";
        """,
        0,
    )

    assert val == 1
    assert "r1" not in r1
    assert "r2" not in r2


def test_eval_incrbyfloat(r: valkey.Redis):
    r.set("foo", 0.5)
    val = r.eval(
        """
        local value = valkey.call("INCRBYFLOAT", KEYS[1], 2.0);
        return type(value) == "string" and tonumber(value) == 2.5;
        """,
        1,
        "foo",
    )
    assert val == 1


def test_eval_lrange(r: valkey.Redis):
    r.rpush("foo", "a", "b")
    val = r.eval(
        """
        local value = valkey.call("LRANGE", KEYS[1], 0, -1);
        return type(value) == "table" and value[1] == "a" and value[2] == "b";
        """,
        1,
        "foo",
    )
    assert val == 1


def test_eval_ltrim(r: valkey.Redis):
    r.rpush("foo", "a", "b", "c", "d")
    val = r.eval(
        """
        local value = valkey.call("LTRIM", KEYS[1], 1, 2);
        return type(value) == "table" and value.ok == "OK";
        """,
        1,
        "foo",
    )
    assert val == 1
    assert r.lrange("foo", 0, -1) == [b"b", b"c"]


def test_eval_lset(r: valkey.Redis):
    r.rpush("foo", "a", "b")
    val = r.eval(
        """
        local value = valkey.call("LSET", KEYS[1], 0, "z");
        return type(value) == "table" and value.ok == "OK";
        """,
        1,
        "foo",
    )
    assert val == 1
    assert r.lrange("foo", 0, -1) == [b"z", b"b"]


def test_eval_sdiff(r: valkey.Redis):
    r.sadd("foo", "a", "b", "c", "f", "e", "d")
    r.sadd("bar", "b")
    val = r.eval(
        """
        local value = valkey.call("SDIFF", KEYS[1], KEYS[2]);
        if type(value) ~= "table" then
            return valkey.error_reply(type(value) .. ", should be table");
        else
            return value;
        end
        """,
        2,
        "foo",
        "bar",
    )
    # Note: while fakevalkey sorts the result when using Lua, this isn't
    # actually part of the valkey contract (see
    # https://github.com/antirez/valkey/issues/5538), and for Redis 5 we
    # need to sort val to pass the test.
    assert sorted(val) == [b"a", b"c", b"d", b"e", b"f"]


def test_script(r: valkey.Redis):
    script = r.register_script("return ARGV[1]")
    result = script(args=[42])
    assert result == b"42"


@testtools.fake_only
def test_lua_log(r, caplog):
    logger = fakevalkey._server.LOGGER
    script = """
        valkey.log(valkey.LOG_DEBUG, "debug")
        valkey.log(valkey.LOG_VERBOSE, "verbose")
        valkey.log(valkey.LOG_NOTICE, "notice")
        valkey.log(valkey.LOG_WARNING, "warning")
    """
    script = r.register_script(script)
    with caplog.at_level("DEBUG"):
        script()
    assert caplog.record_tuples == [
        (logger.name, logging.DEBUG, "debug"),
        (logger.name, logging.INFO, "verbose"),
        (logger.name, logging.INFO, "notice"),
        (logger.name, logging.WARNING, "warning"),
    ]


def test_lua_log_no_message(r: valkey.Redis):
    script = "valkey.log(valkey.LOG_DEBUG)"
    script = r.register_script(script)
    with pytest.raises(valkey.ResponseError):
        script()


@testtools.fake_only
def test_lua_log_different_types(r, caplog):
    logger = logging.getLogger("fakevalkey")
    script = "valkey.log(valkey.LOG_DEBUG, 'string', 1, true, 3.14, 'string')"
    script = r.register_script(script)
    with caplog.at_level("DEBUG"):
        script()
    assert caplog.record_tuples == [(logger.name, logging.DEBUG, "string 1 3.14 string")]


def test_lua_log_wrong_level(r: valkey.Redis):
    script = "valkey.log(10, 'string')"
    script = r.register_script(script)
    with pytest.raises(valkey.ResponseError):
        script()


@testtools.fake_only
def test_lua_log_defined_vars(r, caplog):
    logger = fakevalkey._server.LOGGER
    script = """
        local var='string'
        valkey.log(valkey.LOG_DEBUG, var)
    """
    script = r.register_script(script)
    with caplog.at_level("DEBUG"):
        script()
    assert caplog.record_tuples == [(logger.name, logging.DEBUG, "string")]


def test_hscan_cursors_are_bytes(r: valkey.Redis):
    r.hset("hkey", "foo", 1)

    result = r.eval(
        """
        local results = valkey.call("HSCAN", KEYS[1], "0")
        return results[1]
        """,
        1,
        "hkey",
    )

    assert result == b"0"
    assert isinstance(result, bytes)


@pytest.mark.xfail  # TODO
def test_deleting_while_scan(r: valkey.Redis):
    for i in range(100):
        r.set(f"key-{i}", i)

    assert len(r.keys()) == 100

    script = """
        local cursor = 0
        local seen = {}
        repeat
            local result = valkey.call('SCAN', cursor)
            for _,key in ipairs(result[2]) do
                seen[#seen+1] = key
                valkey.call('DEL', key)
            end
            cursor = tonumber(result[1])
        until cursor == 0
        return seen
    """

    assert len(r.register_script(script)()) == 100
    assert len(r.keys()) == 0
