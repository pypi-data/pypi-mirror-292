import pytest
import pyrin
import blake3
import struct


# TODO: Move to SDK e.g. (add blake3 as dep ?)
def serialize_header(header, for_pre_pow: bool = False) -> bytes:
    hasher = blake3.blake3()

    nonce = 0 if for_pre_pow else header["nonce"]
    timestamp = 0 if for_pre_pow else header["timestamp"]
    num_parents = len(header["parents_by_level"])
    version = header["version"]

    hasher.update(struct.pack("<H", version))
    hasher.update(struct.pack("<Q", num_parents))

    for parent in header["parents_by_level"]:
        hasher.update(struct.pack("<Q", len(parent)))
        for hash_string in parent:
            hasher.update(bytes.fromhex(hash_string))

    hasher.update(bytes.fromhex(header["hash_merkle_root"]))
    hasher.update(bytes.fromhex(header["accepted_id_merkle_root"]))
    hasher.update(bytes.fromhex(header["utxo_commitment"]))

    hasher.update(struct.pack("<Q", timestamp))
    hasher.update(struct.pack("<Q", header["bits"]))
    hasher.update(struct.pack("<Q", nonce))
    hasher.update(struct.pack("<Q", header["daa_score"]))
    hasher.update(struct.pack("<Q", header["blue_score"]))

    blue_work = header["blue_work"]
    hasher.update(struct.pack("<Q", len(blue_work)))
    hasher.update(bytes(blue_work))

    hasher.update(bytes.fromhex(header["pruning_point"]))

    return hasher.digest()


def test_serialize_header():
    header = {
        "version": 1,
        "parents_by_level": [
            ['7cb9a813c1db833032612dd0fc260f06f567ba4b0979c4dba7b17335997b39ed',
             '5204909b97faea4aa356e0a99ae49e8b52757218bb625fd099e5aee4313e4c4f'],
            ['7cb9a813c1db833032612dd0fc260f06f567ba4b0979c4dba7b17335997b39ed',
             '5204909b97faea4aa356e0a99ae49e8b52757218bb625fd099e5aee4313e4c4f'],
            ['7cb9a813c1db833032612dd0fc260f06f567ba4b0979c4dba7b17335997b39ed',
             '5204909b97faea4aa356e0a99ae49e8b52757218bb625fd099e5aee4313e4c4f'],
            ['7cb9a813c1db833032612dd0fc260f06f567ba4b0979c4dba7b17335997b39ed',
             '5204909b97faea4aa356e0a99ae49e8b52757218bb625fd099e5aee4313e4c4f'],
            ['7cb9a813c1db833032612dd0fc260f06f567ba4b0979c4dba7b17335997b39ed',
             '5204909b97faea4aa356e0a99ae49e8b52757218bb625fd099e5aee4313e4c4f'],
            ['7cb9a813c1db833032612dd0fc260f06f567ba4b0979c4dba7b17335997b39ed',
             '5204909b97faea4aa356e0a99ae49e8b52757218bb625fd099e5aee4313e4c4f'],
            ['7cb9a813c1db833032612dd0fc260f06f567ba4b0979c4dba7b17335997b39ed',
             '5204909b97faea4aa356e0a99ae49e8b52757218bb625fd099e5aee4313e4c4f'],
            ['7cb9a813c1db833032612dd0fc260f06f567ba4b0979c4dba7b17335997b39ed',
             '5204909b97faea4aa356e0a99ae49e8b52757218bb625fd099e5aee4313e4c4f'],
            ['5204909b97faea4aa356e0a99ae49e8b52757218bb625fd099e5aee4313e4c4f',
             '7cb9a813c1db833032612dd0fc260f06f567ba4b0979c4dba7b17335997b39ed'],
            ['7cb9a813c1db833032612dd0fc260f06f567ba4b0979c4dba7b17335997b39ed',
             '5204909b97faea4aa356e0a99ae49e8b52757218bb625fd099e5aee4313e4c4f'],
            ['7cb9a813c1db833032612dd0fc260f06f567ba4b0979c4dba7b17335997b39ed',
             '5204909b97faea4aa356e0a99ae49e8b52757218bb625fd099e5aee4313e4c4f'],
            ['7cb9a813c1db833032612dd0fc260f06f567ba4b0979c4dba7b17335997b39ed',
             '5204909b97faea4aa356e0a99ae49e8b52757218bb625fd099e5aee4313e4c4f'],
            ['5204909b97faea4aa356e0a99ae49e8b52757218bb625fd099e5aee4313e4c4f',
             '7cb9a813c1db833032612dd0fc260f06f567ba4b0979c4dba7b17335997b39ed'],
            ['7cb9a813c1db833032612dd0fc260f06f567ba4b0979c4dba7b17335997b39ed',
             '5204909b97faea4aa356e0a99ae49e8b52757218bb625fd099e5aee4313e4c4f'],
            ['7cb9a813c1db833032612dd0fc260f06f567ba4b0979c4dba7b17335997b39ed',
             '5204909b97faea4aa356e0a99ae49e8b52757218bb625fd099e5aee4313e4c4f'],
            ['7cb9a813c1db833032612dd0fc260f06f567ba4b0979c4dba7b17335997b39ed',
             '5204909b97faea4aa356e0a99ae49e8b52757218bb625fd099e5aee4313e4c4f'],
            ['7cb9a813c1db833032612dd0fc260f06f567ba4b0979c4dba7b17335997b39ed',
             '5204909b97faea4aa356e0a99ae49e8b52757218bb625fd099e5aee4313e4c4f'],
            ['7cb9a813c1db833032612dd0fc260f06f567ba4b0979c4dba7b17335997b39ed',
             '5204909b97faea4aa356e0a99ae49e8b52757218bb625fd099e5aee4313e4c4f'],
            ['7cb9a813c1db833032612dd0fc260f06f567ba4b0979c4dba7b17335997b39ed',
             '5204909b97faea4aa356e0a99ae49e8b52757218bb625fd099e5aee4313e4c4f'],
            ['7cb9a813c1db833032612dd0fc260f06f567ba4b0979c4dba7b17335997b39ed',
             '5204909b97faea4aa356e0a99ae49e8b52757218bb625fd099e5aee4313e4c4f'],
            ['139399dad7b16816c745108574d433d23b0dc91f77b65219aca4dd4896bbf8d0'],
            ['3f8336bfefac39e8ccca5e87fdcabcc33da576946d7a0c0697ef48dc9a194a34'],
            ['3f8336bfefac39e8ccca5e87fdcabcc33da576946d7a0c0697ef48dc9a194a34'],
            ['30e8f7d35d39108282d68c962b839ddb1d18eb7e725a4cf2d40edcfa9f9f4651',
             '8c969288c6805abc47e81afc7a1bc24da17193159913db512733e883e6a32d5c'],
            ['4efedc8197980090dd94d19b769e6cd781474404baeebd6b76afbec7c228f726'],
            ['4efedc8197980090dd94d19b769e6cd781474404baeebd6b76afbec7c228f726'],
            ['4efedc8197980090dd94d19b769e6cd781474404baeebd6b76afbec7c228f726'],
            ['0625151e5473868aa43e5078c2f8a0d7106c3ba64c26f47e1b87e8b229b35038'],
            ['0625151e5473868aa43e5078c2f8a0d7106c3ba64c26f47e1b87e8b229b35038'],
            ['0625151e5473868aa43e5078c2f8a0d7106c3ba64c26f47e1b87e8b229b35038'],
            ['77f5b20739b24d7cce099df94ff7e58ac1ed298bba6b0a562ced1479e34c19eb'],
            ['ffd396504deafca0b9938cee2100247c59e96a80c123156ccab026deef650ce4'],
            ['ffd396504deafca0b9938cee2100247c59e96a80c123156ccab026deef650ce4'],
            ['69ded8886078104985c073b4e4dcac9db542df26af5ffd7e51e9650939488267'],
            ['69ded8886078104985c073b4e4dcac9db542df26af5ffd7e51e9650939488267'],
            ['d5bf9cee35c06d4f8b34d75b789b6edddc21f6c3d0e10733a67c8ab52841dff3'],
            ['d5bf9cee35c06d4f8b34d75b789b6edddc21f6c3d0e10733a67c8ab52841dff3'],
            ['c19be16f2c295ca30cc74c60bde5ef21d2f4c8c28fcec75f910506cd6cfdc489'],
            ['70913d679d5148d42d8d502321c05935e277706998057c505d38a261a04b1e47'],
            ['f9a730fcb7f5faf52ae1964eca8c8f1f0003510335a274f8c5d42404f54af647'],
            ['f9a730fcb7f5faf52ae1964eca8c8f1f0003510335a274f8c5d42404f54af647']
        ],
        "hash_merkle_root": "3b5dc0d152e31332c90c2c845f3189d42938983df10bf28b7b961c3d55bda6fa",
        "accepted_id_merkle_root": "0ad6af42cbddb4993e33ca58ab7c0c027ab898c3bfa277fd4402f507729cead1",
        "utxo_commitment": "438df8bc9acc591d375bfd257e647aa252c60a8c6a364b27f4ad728cc41fee97",
        "timestamp": 1724257062156,
        "bits": 441217259,
        "nonce": 8078885133799864693,
        "daa_score": 23439639,
        "blue_work": [78, 172, 55, 221, 251, 110, 69, 86, 242, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        "blue_score": 21907860,
        "pruning_point": "3d987893df6c47b9ae87cc013b5d0b35d21156781573e4cd8b4ac7a2172a365d",
    }

    result = serialize_header(header)
    assert result.hex() == "54f86d92da8d545c35206e36beb4223ef534d2eb2b3d916ccba113d68dbd2570"
