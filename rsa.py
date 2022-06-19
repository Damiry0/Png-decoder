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
        self.init_vec = random.getrandbits(self.public_key[0].bit_length())

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

    def encrypt_cbc(self, data):
        key_size = self.public_key[0].bit_length()
        block_size = key_size // 8 - 1
        encrypted_data = bytearray()
        filler = bytearray()
        empty = 0
        while self.init_vec.bit_length() != key_size:
            self.init_vec = random.getrandbits(self.public_key[0].bit_length())
        prev_vec = self.init_vec

        for i in range(0, len(data), block_size):
            block_bytes = bytes(data[i:i + block_size])  # pobranie dobrej wielkości bloku

            if len(block_bytes) % block_size != 0:  # wypełnianie zerami ostatniego niepelnego
                for empty in range(block_size - (len(block_bytes) % block_size)):
                    filler.append(0)
                block_bytes = filler + block_bytes

            prev_vec = prev_vec.to_bytes(block_size + 1, 'big')  # zamiana wektorow i dopasowanie dlugosci
            prev_vec = int.from_bytes(prev_vec[:len(block_bytes)], 'big')

            xor = int.from_bytes(block_bytes, 'big') ^ prev_vec
            encrypt_int_block = pow(xor, self.public_key[1], self.public_key[0])  # szyfrowanie
            prev_vec = encrypt_int_block
            encrypt_bytes_block = encrypt_int_block.to_bytes(block_size + 1, 'big')

            encrypted_data += encrypt_bytes_block

        return encrypted_data, empty

    def decrypt_cbc(self, encrypted_data, empty):
        key_size = self.private_key[0].bit_length()
        decrypted_data = bytearray()
        block_size = key_size // 8
        prev_vec = self.init_vec

        for i in range(0, len(encrypted_data), block_size):
            encrypted_bytes_block = encrypted_data[i:i + block_size]  # pobranie dobrej wielkości bloku
            encrypted_int_block = int.from_bytes(encrypted_bytes_block, 'big')
            decrypted_int_block = pow(encrypted_int_block, self.private_key[1], self.private_key[0])  # deszyfrowanie

            prev_vec = prev_vec.to_bytes(block_size, 'big')  # przygotowanie wektora i xor
            prev_vec = int.from_bytes(prev_vec[:block_size - 1], 'big')
            xor = prev_vec ^ decrypted_int_block

            decrypted_bytes_block = xor.to_bytes(block_size - 1, 'big')
            if i + block_size >= len(encrypted_data):  # ewentualne usuniecie leading zeros
                decrypted_bytes_block = decrypted_bytes_block[empty + 1:]
            decrypted_data += decrypted_bytes_block

            prev_vec = int.from_bytes(encrypted_bytes_block, 'big')  # podmiana wektora

        return decrypted_data

    def encrypt(self, mess):
        return pow(mess, self.public_key[1], self.public_key[0])

    def decrypt(self, mess):
        return pow(mess, self.private_key[1], self.private_key[0])


if __name__ == '__main__':
    randomRsa = RSA(64)
    print(f"public key = {randomRsa.public_key}")
    print(f"priavte key = {randomRsa.private_key}")
    addr = r'C:\Users\Karolina\Desktop\Karolina\Studia\3 rok\6 sem\E-media\Png-decoder\Graphics\cubes.png'
    addr2 = "/home/damiry/Documents/GitHub/Png-decoder/Graphics/cubes.png"

    example = png.Png(addr)
    if example.check_signature():
        chunk_names = example.read_all_chunks()
        Width, Height, Bit_depth, Color_type, Compression_method, Filter_method, Interlace_method = example.parse_IHDR()
        image = example.parse_IDAT(Height, Width)
        working = example.IDAT_chunk_processor_cbc()
        example.save_file("cbc_please_work", working)
