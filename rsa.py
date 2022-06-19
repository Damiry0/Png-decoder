import random
import png
from keys import Keys


class RSA:

    def __init__(self, public_key, private_key):
        self.public_key = public_key
        self.private_key = private_key

    def power(self, x, m, n):
        a = 1
        while m > 0:
            if m % 2 == 1:
                a = (a * x) % n
            x = (x * x) % n
            m //= 2
        return a

    def encrypting(self, num):
        result = self.power(num, self.public_key['e'], self.public_key['n'])
        return result

    def decrypting(self, num):
        result = self.power(num, self.private_key['d'], self.private_key['n'])
        return result

    def ecb_encrypt(self, IDAT_data):
        key_size = self.public_key['n'].bit_length()
        block_size = key_size // 8 - 1
        encrypted_data = bytearray()
        padding = bytearray()
        after_iend_data = bytearray()
        empty = 0

        for i in range(0, len(IDAT_data), block_size):
            bytes_block = bytes(IDAT_data[i:i + block_size])

            # padding
            if len(bytes_block) % block_size != 0:
                for empty in range(block_size - (len(bytes_block) % block_size)):
                    padding.append(0)
                bytes_block = padding + bytes_block

            int_block = int.from_bytes(bytes_block, 'big')
            encrypt_block_int = self.encrypting(int_block)
            encrypt_block_bytes = encrypt_block_int.to_bytes(block_size + 1, 'big')

            # after_iend_data.append(encrypt_block_bytes[-1])
            # encrypt_block_bytes = encrypt_block_bytes[:-1]
            encrypted_data += encrypt_block_bytes

        return encrypted_data, empty

    def ecb_decrypt(self, encrypted_data, after_iend_data):
        key_size = self.private_key['n'].bit_length()
        decrypted_data = bytearray()
        block_size = key_size // 8
        k = 0

        for i in range(0, len(encrypted_data), block_size):
            encrypted_block_bytes = encrypted_data[i:i + block_size]
            encrypted_block_int = int.from_bytes(encrypted_block_bytes, 'big')

            decrypted_block_int = self.decrypting(encrypted_block_int)
            decrypted_block_bytes = decrypted_block_int.to_bytes(block_size, 'big')

            decrypted_data += decrypted_block_bytes
            k += 1
        return decrypted_data

    def cbc_encrypt(self, IDAT_data):
        key_size = self.public_key['n'].bit_length()
        block_size = key_size // 8 - 1
        encrypted_data = bytearray()
        padding = bytearray()
        after_iend_data = bytearray()
        self.vectorIV = random.getrandbits(key_size)
        previous_vector = self.vectorIV

        for i in range(0, len(IDAT_data), block_size):
            bytes_block = bytes(IDAT_data[i:i + block_size])

            # padding
            if len(bytes_block) % block_size != 0:
                for empty in range(block_size - (len(bytes_block) % block_size)):
                    padding.append(0)
                bytes_block = padding + bytes_block

            previous_vector = previous_vector.to_bytes(block_size + 1, 'big')
            previous_vector = int.from_bytes(previous_vector[:len(bytes_block)], 'big')

            xor = int.from_bytes(bytes_block, 'big') ^ previous_vector
            encrypt_block_int = self.encrypting(xor)
            previous_vector = encrypt_block_int
            encrypt_block_bytes = encrypt_block_int.to_bytes(block_size + 1, 'big')

            after_iend_data.append(encrypt_block_bytes[-1])
            encrypt_block_bytes = encrypt_block_bytes[:-1]
            encrypted_data += encrypt_block_bytes

        return encrypted_data, after_iend_data

    def cbc_decrypt(self, encrypted_data, empty):
        key_size = self.private_key['n'].bit_length()
        decrypted_data = bytearray()
        block_size = key_size // 8 - 1
        previous_vector = self.vectorIV
        k = 0

        for i in range(0, len(encrypted_data), block_size):
            encrypted_block_bytes = encrypted_data[i:i + block_size]
            encrypted_block_int = int.from_bytes(encrypted_block_bytes, 'big')
            decrypted_block_int = self.decrypting(encrypted_block_int)

            previous_vector = previous_vector.to_bytes(block_size, 'big')
            previous_vector = int.from_bytes(previous_vector[:block_size], 'big')
            xor = previous_vector ^ decrypted_block_int

            decrypted_block_bytes = xor.to_bytes(block_size, 'big')
            decrypted_data += decrypted_block_bytes

            previous_vector = int.from_bytes(encrypted_block_bytes, 'big')
            k += 1

        return decrypted_data


if __name__ == '__main__':
    example = png.Png("/home/damiry/Documents/GitHub/Png-decoder/Graphics/cubes.png")
    if example.check_signature():
        chunk_names = example.read_all_chunks()
        Width, Height, Bit_depth, Color_type, Compression_method, Filter_method, Interlace_method = example.parse_IHDR()
        please_work = example.get_IDAT()
        keys = Keys(256)
        public_key = keys.generate_public_key()
        private_key = keys.generate_private_key()
        rsa = RSA(public_key, private_key)
        encrypt_data, after_iend_dataaa = rsa.ecb_encrypt(please_work)
        LETSGO = example.parse_IDAT_ECB(180, 240, encrypt_data)
        decrypt_data = rsa.ecb_decrypt(LETSGO, after_iend_dataaa)
        example.create_ecb_image_2(decrypt_data)
