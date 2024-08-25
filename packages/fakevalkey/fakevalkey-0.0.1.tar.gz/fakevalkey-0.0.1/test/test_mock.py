from unittest.mock import patch

import valkey

from fakevalkey import FakeValkey


def test_mock():
    # Mock Redis connection
    def bar(redis_host: str, redis_port: int):
        valkey.Redis(redis_host, redis_port)

    with patch("valkey.Redis", FakeValkey):
        # Call function
        bar("localhost", 6000)

        # Related to #36 - this should fail if mocking Redis does not work
