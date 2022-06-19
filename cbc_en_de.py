import random
import rsa
import png


@staticmethod
def encrypt_cbc(data, public_key, iv):
    key_size = public_key[0].bit_length()
    encrypted_data = bytearray()
    step = key_size // 8 - 1
    padding = bytearray()
    previous = iv

    print(f"First Initialization Vector: {previous}")
    for i in range(0, len(data), step):
        raw_data_bytes = bytes(data[i:i + step])

        # padding
        if len(raw_data_bytes) % step != 0:
            for empty in range(step - (len(raw_data_bytes) % step)):
                padding.append(0)
            raw_data_bytes = padding + raw_data_bytes

        previous = previous.to_bytes(step + 1, 'big')
        previous = int.from_bytes(previous[:len(raw_data_bytes)], 'big')
        xor = int.from_bytes(raw_data_bytes, 'big') ^ previous

        encrypted_data_int = pow(xor, public_key[1], public_key[0])
        previous = encrypted_data_int
        encrypted_data_bytes = encrypted_data_int.to_bytes(step + 1, 'big')

        """for encrypted_byte in encrypted_data_bytes:
            encrypted_data.append(encrypted_byte)"""
    return encrypted_data_bytes


@staticmethod
def decrypt_cbc(data, private_key, initialization_vector):
    key_size = private_key[0].bit_length()
    decrypted_data = bytearray()
    step = key_size // 8
    previous = initialization_vector

    for i in range(0, len(data), step):
        encrypted_bytes = b''
        for byte in data[i:i + step]:
            encrypted_bytes += byte.to_bytes(1, 'big')

        encrypted_data_int = int.from_bytes(encrypted_bytes, 'big')
        decrypted_data_int = pow(encrypted_data_int, private_key[1], private_key[0])

        previous = previous.to_bytes(step, 'big')
        previous = int.from_bytes(previous[:step - 1], 'big')
        xor = previous ^ decrypted_data_int

        decrypted_data_bytes = xor.to_bytes(step, 'big')
        decr = int.from_bytes(decrypted_data_bytes, 'big')
        decr_size = decr.bit_length() // 8
        decrypted_data_bytes = decr.to_bytes(decr_size + 1, 'big')
        '''for decrypted_byte in decrypted_data_bytes:
            decrypted_data.append(decrypted_byte)'''

        previous = int.from_bytes(encrypted_bytes, 'big')
    return decrypted_data_bytes


if __name__ == '__main__':
    addr = r'C:\Users\Karolina\Desktop\Karolina\Studia\3 rok\6 sem\E-media\Png-decoder\Graphics\5.png'
    plaintext = b'\x01\xca\xc5\xe9\xff\x00\x01\x01\x00\x01\x01\x01\x00\x01\x00\x01\x00\xff\x00\x00\x00\x02\x01\x01\x00'
    idat_chunk = png.ret_IDAT_noncomp(addr)
    randomRsa = rsa.RSA(128)
    pubkey = randomRsa.public_key
    privkey = randomRsa.private_key
    iv = random.getrandbits(pubkey[0].bit_length())
    while iv.bit_length() != pubkey[0].bit_length():
        iv = random.getrandbits(pubkey[0].bit_length())
    # print(f"{privkey, pubkey}")

    # print(f"Original data (bytes): {plaintext}")
    print()
    xd = encrypt_cbc(plaintext, pubkey, iv)
    print(f"Encrypted data (bytes): {xd}")
    print()
    res = decrypt_cbc(xd, privkey, iv)
    print(f"Decrypted data?? (bytes): {res}")
    '''if res == plaintext:
        print("yay")
    else:
        print("nay")'''
