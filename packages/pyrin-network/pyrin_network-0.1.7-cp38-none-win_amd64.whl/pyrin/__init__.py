import struct

from .pyrin import *

from .uint256 import compact_to_big
from .xoshiro256plusplus import XoShiRo256PlusPlus

__doc__ = pyrin.__doc__
if hasattr(pyrin, "__all__"):
    __all__ = pyrin.__all__

# Add your Python functions and classes here
# def python_function(x):
#     return x + 10
#
# class PyrinWrapper:
#     def __init__(self):
#         # Initialize with Rust objects if needed
#         pass
#
#     def combined_function(self, value):
#         # Use both Rust and Python functions
#         rust_result = _pyrin.rust_function(value)
#         return python_function(rust_result)
#

def uint192_from_bytes(byte_array):
    # Ensure we have 24 bytes
    if len(byte_array) != 24:
        raise ValueError("Byte array must be 24 bytes long")

    # Convert from little-endian byte array to integer
    return int.from_bytes(byte_array, byteorder="little", signed=False)

# def serialize_header(header, for_pre_pow: bool = False) -> bytes:
#     hasher = blake3.blake3()
#
#     nonce = 0 if for_pre_pow else header.nonce
#     timestamp = 0 if for_pre_pow else header.timestamp
#     num_parents = len(header.parents_by_level)
#     version = header.version
#
#     hasher.update(struct.pack("<H", version))
#     hasher.update(struct.pack("<Q", num_parents))
#
#     for parent in header.parents_by_level:
#         hasher.update(struct.pack("<Q", len(parent)))
#         for hash_string in parent:
#             hasher.update(bytes.fromhex(hash_string))
#
#     hasher.update(bytes.fromhex(header.hash_merkle_root))
#     hasher.update(bytes.fromhex(header.accepted_id_merkle_root))
#     hasher.update(bytes.fromhex(header.utxo_commitment))
#
#     hasher.update(struct.pack("<Q", timestamp))
#     hasher.update(struct.pack("<Q", header.bits))
#     hasher.update(struct.pack("<Q", nonce))
#     hasher.update(struct.pack("<Q", header.daa_score))
#     hasher.update(struct.pack("<Q", header.blue_score))
#
#     blue_work = header.blue_work
#     hasher.update(struct.pack("<Q", len(blue_work)))
#     hasher.update(bytes(blue_work))
#
#     hasher.update(bytes.fromhex(header.pruning_point))
#
#     return hasher.digest()