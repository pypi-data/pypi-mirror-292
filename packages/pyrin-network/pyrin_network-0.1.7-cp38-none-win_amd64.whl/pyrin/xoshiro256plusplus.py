
class XoShiRo256PlusPlus:
    def __init__(self, hash_value):
        # Assuming hash_value is a list or tuple of 4 64-bit integers
        self.s0 = hash_value[0]
        self.s1 = hash_value[1]
        self.s2 = hash_value[2]
        self.s3 = hash_value[3]

    def u64(self):
        result = (self.s0 + ((self.s0 + self.s3) & 0xFFFFFFFFFFFFFFFF)) & 0xFFFFFFFFFFFFFFFF
        result = (result + ((result << 23) | (result >> 41))) & 0xFFFFFFFFFFFFFFFF

        t = (self.s1 << 17) & 0xFFFFFFFFFFFFFFFF

        self.s2 ^= self.s0
        self.s3 ^= self.s1
        self.s1 ^= self.s2
        self.s0 ^= self.s3

        self.s2 ^= t
        self.s3 = ((self.s3 << 45) | (self.s3 >> 19)) & 0xFFFFFFFFFFFFFFFF

        return result
