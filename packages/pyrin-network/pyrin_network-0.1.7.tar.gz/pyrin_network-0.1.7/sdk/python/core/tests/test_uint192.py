import pytest
import pyrin

def test_uint192_from_bytes():
    assert pyrin.uint192_from_bytes(
        [107, 48, 244, 242, 39, 227, 245, 35, 242, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    ) == 13911436258498342826091
