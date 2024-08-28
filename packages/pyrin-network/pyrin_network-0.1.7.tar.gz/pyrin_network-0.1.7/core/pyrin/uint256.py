


def compact_to_big(compact: int) -> int:
    """
    CompactToBig converts a compact representation of a whole number N to an
    unsigned 32-bit number. The representation is similar to IEEE754 floating
    point numbers.

    Like IEEE754 floating point, there are three basic components: the sign,
    the exponent, and the mantissa. They are broken out as follows:

      - the most significant 8 bits represent the unsigned base 256 exponent
      - bit 23 (the 24th bit) represents the sign bit
      - the least significant 23 bits represent the mantissa

        -------------------------------------------------
        |   Exponent     |    Sign    |    Mantissa     |
        -------------------------------------------------
        | 8 bits [31-24] | 1 bit [23] | 23 bits [22-00] |
        -------------------------------------------------

    The formula to calculate N is:

     N = (-1^sign) * mantissa * 256^(exponent-3)
    """
    # Extract the mantissa, sign bit, and exponent.
    mantissa = compact & 0x007fffff
    is_negative = (compact & 0x00800000) != 0
    exponent = compact >> 24

    # Since the base for the exponent is 256, the exponent can be treated
    # as the number of bytes to represent the full 256-bit number. So,
    # treat the exponent as the number of bytes and shift the mantissa
    # right or left accordingly. This is equivalent to:
    # N = mantissa * 256^(exponent-3)
    if exponent <= 3:
        mantissa >>= 8 * (3 - exponent)
        result = mantissa
    else:
        result = mantissa << (8 * (exponent - 3))

    # Make it negative if the sign bit is set.
    if is_negative:
        result = -result

    return result


# def from_compact_target(bits):
#     # Decoding the mantissa and exponent
#     unshifted_expt = bits >> 24
#     if unshifted_expt <= 3:
#         mant = (bits & 0xFFFFFF) >> (8 * (3 - unshifted_expt))
#         expt = 0
#     else:
#         mant = bits & 0xFFFFFF
#         expt = 8 * (unshifted_expt - 3)
#
#     # Check if mantissa is too large (> 0x7FFFFF)
#     if mant > 0x7FFFFF:
#         return Uint256(0)  # Assuming Uint256(0) is equivalent to Default::default()
#     else:
#         # Shifting left by expt
#         return Uint256.from_u64(mant) << expt
#
# class Uint256:
#     def __init__(self, value):
#         self.value = value & ((1 << 256) - 1)  # Ensure 256-bit value
#
#     @classmethod
#     def from_u64(cls, value):
#         return cls(value)
#
#     def __lshift__(self, shift):
#         return Uint256(self.value << shift)
#
#     def __str__(self):
#         return hex(self.value)
#
#     def to_le_bytes(self):
#         # return self.value.to_bytes(32, "little")
#         return list(self.value.to_bytes(32, 'little'))
#
#     # def to_le_bytes(self):
#     #     byte_array = []
#     #     value = self.value
#     #     for _ in range(32):
#     #         byte_array.append(value & 0xFF)
#     #         value >>= 8
#     #     return byte_array