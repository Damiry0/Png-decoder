import random
import rsa
import png


def cbc_encrypt(IDAT_data, public_key, IV):
    key_size = public_key[0].bit_length()
    block_size = key_size // 8 - 1
    encrypted_data = bytearray()
    padding = bytearray()
    after_iend_data = bytearray()
    vectorIV = IV
    previous_vector = vectorIV
    datalrn = len(IDAT_data)
    empty = 0

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
        encrypt_block_int = pow(xor, public_key[1], public_key[0])
        previous_vector = encrypt_block_int
        encrypt_block_bytes = encrypt_block_int.to_bytes(block_size + 1, 'big')

        after_iend_data.append(encrypt_block_bytes[-1])
        encrypt_block_bytes = encrypt_block_bytes[:-1]
        encrypted_data += encrypt_block_bytes

    print()
    return encrypted_data, after_iend_data, empty


def cbc_decrypt(encrypted_data, after_iend_data, iv, private_key, empty):
    key_size = private_key[0].bit_length()
    decrypted_data = bytearray()
    block_size = key_size // 8 - 1
    previous_vector = iv
    k = 0
    ed = len(encrypted_data)

    for i in range(0, len(encrypted_data), block_size):
        encrypted_block_bytes = encrypted_data[i:i + block_size] + after_iend_data[k].to_bytes(1, 'big')
        encrypted_block_int = int.from_bytes(encrypted_block_bytes, 'big')
        decrypted_block_int = pow(encrypted_block_int, private_key[1], private_key[0])

        previous_vector = previous_vector.to_bytes(block_size + 1, 'big')
        previous_vector = int.from_bytes(previous_vector[:block_size], 'big')
        xor = previous_vector ^ decrypted_block_int

        decrypted_block_bytes = xor.to_bytes(block_size, 'big')
        if i + block_size >= len(encrypted_data):
            decrypted_block_bytes = decrypted_block_bytes[empty+1:]
        decrypted_data += decrypted_block_bytes

        previous_vector = int.from_bytes(encrypted_block_bytes, 'big')
        k += 1
    print()
    return decrypted_data


if __name__ == '__main__':
    addr = r'C:\Users\Karolina\Desktop\Karolina\Studia\3 rok\6 sem\E-media\Png-decoder\Graphics\5.png'


    idat_chunk = png.ret_IDAT_noncomp(addr)
    randomRsa = rsa.RSA(128)
    pubkey = randomRsa.public_key
    privkey = randomRsa.private_key
    iv = random.getrandbits(pubkey[0].bit_length())
    while iv.bit_length() != pubkey[0].bit_length():
        iv = random.getrandbits(pubkey[0].bit_length())
    # print(f"{privkey, pubkey}")

    # print(f"Original data (bytes): {plaintext}")
    #print()
    #xd, ech, e = cbc_encrypt(plaintext, pubkey, iv)

    example = png.Png(addr)
    if example.check_signature():
        chunk_names = example.read_all_chunks()
        Width, Height, Bit_depth, Color_type, Compression_method, Filter_method, Interlace_method = example.parse_IHDR()
        image = example.parse_IDAT(Height, Width)
        working = example.IDAT_chunk_processor_cbc()
        example.save_file("cbc_please_work", working)

    '''#print(f"Encrypted data (bytes): {xd}")
    #print()
    res = cbc_decrypt(xd, ech, iv, privkey, e)
    #print(f"Decrypted data?? (bytes): {res}")
    if res == plaintext:
        print("yay")
    else:
        print("nay")'''
