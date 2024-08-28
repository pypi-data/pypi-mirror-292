import pytest
import pyrin

def test_xoshiro256plusplus():
    v = bytes.fromhex("26959535291011309493156476344723991336010898738574164086137773096960")
    result = pyrin.xoshiro256plusplus.XoShiRo256PlusPlus(v)
    assert result.u64() == 1082130561
    assert result.u64() == 5629501782362892
    assert result.u64() == 102668011176990624
    assert result.u64() == 4823647870185137019

