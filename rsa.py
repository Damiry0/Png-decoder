import random

import numpy as np
from matplotlib import pyplot as plt

import png


class RSA:
    def __init__(self, bits):
        self.p = self.generatePrimeNumber(bits)
        self.q = self.generatePrimeNumber(bits)
        self.n = self.p * self.q
        self.euler_totient = (self.p - 1) * (self.q - 1)
        self.e = self.calculate_e(self.p, self.q)
        self.d = pow(self.e, -1, self.euler_totient)
        self.public_key = (self.n, self.e)
        self.private_key = (self.n, self.d)
        self.key_size = bits

    def generatePrimeNumber(self, bits):
        while True:
            number = self.nRandomNumber(bits)
            if not self.isMillerRabinPassed(number):
                continue
            else:
                return number

    def nRandomNumber(self, n):
        # uses os.urandom() which is fit for cryptography random number generation
        return random.SystemRandom().randint(2 ** (n - 1) + 1, 2 ** n - 1)

    @staticmethod
    def isMillerRabinPassed(mrc):
        # Run 20 iterations of Rabin Miller Primality test
        maxDivisionsByTwo = 0
        ec = mrc - 1
        while ec % 2 == 0:
            ec >>= 1
            maxDivisionsByTwo += 1
        assert (2 ** maxDivisionsByTwo * ec == mrc - 1)

        def trialComposite(round_tester):
            if pow(round_tester, ec, mrc) == 1:
                return False
            for i in range(maxDivisionsByTwo):
                if pow(round_tester, 2 ** i * ec, mrc) == mrc - 1:
                    return False
            return True

        # Set number of trials here
        numberOfRabinTrials = 20
        for i in range(numberOfRabinTrials):
            round_tester = random.randrange(2, mrc)
            if trialComposite(round_tester):
                return False
        return True

    def calculate_e(self, p, q):
        phi = (p - 1) * (q - 1)
        if phi > 65537:
            return 65537  # 2^16+1 prime number
        else:
            e = phi - 1
            while True:
                if self.isMillerRabinPassed(e): return e
                e = e - 2

    def encrypt_ecb(self, data):
        key_size = self.public_key[0].bit_length()
        encrypted_data = bytearray()
        step = key_size // 8 - 1
        padding = bytearray()

        for i in range(0, len(data), step):
            raw_data_bytes = bytes(data[i:i + step])
            if len(raw_data_bytes) % step != 0:  # padding
                for empty in range(step - (len(raw_data_bytes) % step)):
                    padding.append(0)
                    raw_data_bytes = padding + raw_data_bytes

            raw_data_int = int.from_bytes(raw_data_bytes, 'big')
            encrypted_data_int = self.encrypt(raw_data_int)
            encrypted_data_bytes = encrypted_data_int.to_bytes(step, 'big')
            for encrypted_byte in encrypted_data_bytes:
                encrypted_data.append(encrypted_byte)
        return encrypted_data

    def decrypt_ecb(self, data):
        key_size = self.private_key[0].bit_length()
        decrypted_data = []
        step = key_size // 8

        for i in range(0, len(data), step):
            encrypted_bytes = b''
            for byte in data[i:i + step]:
                encrypted_bytes += byte.to_bytes(1, 'big')
            encrypted_data_int = int.from_bytes(encrypted_bytes, 'big')
            decrypted_data_int = self.decrypt(encrypted_data_int)
            decrypted_data_bytes = decrypted_data_int.to_bytes(step - 1, 'big')
            for decrypted_byte in decrypted_data_bytes:
                decrypted_data.append(decrypted_byte)
        return decrypted_data

    def encrypt(self, mess):
        return pow(mess, self.public_key[1], self.public_key[0])

    def decrypt(self, mess):
        return pow(mess, self.private_key[1], self.private_key[0])


if __name__ == '__main__':
    randomRsa = RSA(64)
    print(f"public key = {randomRsa.public_key}")
    print(f"priavte key = {randomRsa.private_key}")

    example = png.Png("/home/damiry/Documents/GitHub/Png-decoder/Graphics/cubes.png")
    if example.check_signature():
        chunk_names = example.read_all_chunks()
        Width, Height, Bit_depth, Color_type, Compression_method, Filter_method, Interlace_method = example.parse_IHDR()
        image = example.parse_IDAT(Height, Width)
        working = example.IDAT_chunk_processor_ecb()
        example.save_file("ecb_please_work", working)
