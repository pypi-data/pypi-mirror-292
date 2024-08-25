from ._connection import (
    FakeValkey,
    FakeStrictValkey,
    FakeConnection,
)
from ._server import FakeServer
from .aioredis import (
    FakeValkey as FakeAsyncRedis,
    FakeConnection as FakeAsyncConnection,
)

try:
    from importlib import metadata
except ImportError:  # for Python < 3.8
    import importlib_metadata as metadata  # type: ignore
__version__ = metadata.version("fakevalkey")
__author__ = "Daniel Moran"
__maintainer__ = "Daniel Moran"
__email__ = "daniel@moransoftware.ca"
__license__ = "BSD-3-Clause"
__url__ = "https://github.com/cunla/fakevalkey-py"
__bugtrack_url__ = "https://github.com/cunla/fakevalkey-py/issues"

__all__ = [
    "FakeServer",
    "FakeValkey",
    "FakeStrictValkey",
    "FakeConnection",
    "FakeAsyncRedis",
    "FakeAsyncConnection",
]
