import random

'''from Crypto.Util import number
from Crypto.PublicKey import RSA as rsa_l
from Crypto.Cipher import PKCS1_OAEP
from numpy import byte'''


class RSA:

    def __init__(self, public_key, private_key):
        self.init_vec = None
        self.public_key = public_key
        self.private_key = private_key

    def encrypting(self, num):
        return pow(num, self.public_key['e'], self.public_key['n'])

    def decrypting(self, num):
        return pow(num, self.private_key['d'], self.private_key['n'])

    def ecb_encrypt(self, data):
        key_size = self.public_key['n'].bit_length()
        block_size = key_size // 8 - 1
        encrypted_data = bytearray()
        filler = bytearray()
        addit_data = bytearray()

        for i in range(0, len(data), block_size):
            bytes_block = bytes(data[i:i + block_size])

            if len(bytes_block) % block_size != 0:
                for empty in range(block_size - (len(bytes_block) % block_size)):
                    filler.append(0)
                bytes_block = filler + bytes_block

            int_block = int.from_bytes(bytes_block, 'big')
            encrypt_int_block = self.encrypting(int_block)
            encrypt_bytes_block = encrypt_int_block.to_bytes(block_size + 1, 'big')

            addit_data.append(encrypt_bytes_block[-1])
            encrypt_bytes_block = encrypt_bytes_block[:-1]
            encrypted_data += encrypt_bytes_block
        return encrypted_data, addit_data

    def ecb_decrypt(self, encrypted_data, addit_data):
        key_size = self.private_key['n'].bit_length()
        decrypted_data = bytearray()
        block_size = key_size // 8 - 1
        k = 0

        for i in range(0, len(encrypted_data), block_size):
            encrypted_block_bytes = encrypted_data[i:i + block_size] + addit_data[k].to_bytes(1, 'big')
            encrypted_int_block = int.from_bytes(encrypted_block_bytes, 'big')

            decrypted_int_block = self.decrypting(encrypted_int_block)
            decrypted_bytes_block = decrypted_int_block.to_bytes(block_size, 'big')

            decrypted_data += decrypted_bytes_block
            k += 1
        return decrypted_data

    def cbc_encrypt(self, data):
        key_size = self.public_key['n'].bit_length()
        block_size = key_size // 8 - 1
        encrypted_data = bytearray()
        filler = bytearray()
        addit_data = bytearray()
        self.init_vec = random.getrandbits(key_size)
        prev_vec = self.init_vec

        for i in range(0, len(data), block_size):
            bytes_block = bytes(data[i:i + block_size])

            if len(bytes_block) % block_size != 0:
                for empty in range(block_size - (len(bytes_block) % block_size)):
                    filler.append(0)
                bytes_block = filler + bytes_block

            prev_vec = prev_vec.to_bytes(block_size + 1, 'big')
            prev_vec = int.from_bytes(prev_vec[:len(bytes_block)], 'big')

            xor = int.from_bytes(bytes_block, 'big') ^ prev_vec
            encrypt_int_block = self.encrypting(xor)
            prev_vec = encrypt_int_block
            encrypt_bytes_block = encrypt_int_block.to_bytes(block_size + 1, 'big')

            addit_data.append(encrypt_bytes_block[-1])
            encrypt_bytes_block = encrypt_bytes_block[:-1]
            encrypted_data += encrypt_bytes_block

        return encrypted_data, addit_data

    def cbc_decrypt(self, encrypted_data, addit_data):
        key_size = self.private_key['n'].bit_length()
        decrypted_data = bytearray()
        block_size = key_size // 8 - 1
        prev_vec = self.init_vec
        k = 0

        for i in range(0, len(encrypted_data), block_size):
            encrypted_bytes_block = encrypted_data[i:i + block_size] + addit_data[k].to_bytes(1, 'big')
            encrypted_int_block = int.from_bytes(encrypted_bytes_block, 'big')
            decrypted_int_block = self.decrypting(encrypted_int_block)

            prev_vec = prev_vec.to_bytes(block_size + 1, 'big')
            prev_vec = int.from_bytes(prev_vec[:block_size], 'big')
            xor = prev_vec ^ decrypted_int_block

            decrypted_bytes_block = xor.to_bytes(block_size, 'big')
            decrypted_data += decrypted_bytes_block

            prev_vec = int.from_bytes(encrypted_bytes_block, 'big')
            k += 1

        return decrypted_data

    '''def crypto_library_encrypt(self, data):
        keys_library = rsa_l.construct((self.public_key['n'], self.public_key['e']))
        encoder_library = PKCS1_OAEP.new(keys_library)
        key_size = self.public_key['n'].bit_length()
        block_size = key_size // 16 - 1
        encrypted_data = bytearray()
        addit_data = bytearray()

        for i in range(0, len(data), block_size):
            bytes_block = bytes(data[i:i + block_size])
            encrypt_bytes_block = encoder_library.encrypt(bytes_block)

            addit_data.append(encrypt_bytes_block[-1])
            encrypt_bytes_block = encrypt_bytes_block[:-1]
            encrypted_data += encrypt_bytes_block

        return encrypted_data, addit_data'''
