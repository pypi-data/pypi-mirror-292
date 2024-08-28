import pytest
import pyrin

def test_uint256():
    compact_target = 0x1d00ffff  # A common difficulty target in Bitcoin

    result = pyrin.uint256.compact_to_big(compact_target)
    assert str(result) == "26959535291011309493156476344723991336010898738574164086137773096960"

