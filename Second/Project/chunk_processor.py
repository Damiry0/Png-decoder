import zlib
import struct
import os
from chunk import Chunk
from pathlib import Path

from keys import Keys
from rsa import RSA
from critical_chunks_data import IHDRData


class PNGChunkProcessor:
    PNG_SIGNATURE = b'\x89PNG\r\n\x1a\n'
    CRITICAL_CHUNKS = [b'IHDR', b'IDAT', b'IEND']

    def __init__(self):
        self.chunks = []
        self.encrypted_data = bytearray()
        self.addit_data = bytearray()
        self.decrypted_data = bytearray()
        self.encrypted_data_from_library = bytearray()
        self.addit_data_from_library = bytearray()

    @staticmethod
    def validate_png(img):
        if (img.read(len(PNGChunkProcessor.PNG_SIGNATURE))
                != PNGChunkProcessor.PNG_SIGNATURE):
            raise Exception('Invalid PNG Signature')

    def save_chunks(self, img):
        self.validate_png(img)
        while True:
            new_chunk = Chunk(img)
            self.chunks.append(new_chunk)
            if new_chunk.chunk_type == b'IEND':
                break

    def IHDR_chunk_processor(self):
        IHDR_data = self.chunks[0].chunk_data
        IHDR_data_values = struct.unpack('>IIBBBBB', IHDR_data)
        IHDR_data = IHDRData(IHDR_data_values)
        self.width = IHDR_data.get_width()
        self.height = IHDR_data.get_height()
        self.color_type = IHDR_data.get_color_type()
        self.bit_depth = IHDR_data.get_bit_depth()

    def IDAT_chunk_processor_ecb(self):
        IDAT_data = b''.join(chunk.chunk_data for chunk in self.chunks
                             if chunk.chunk_type == b'IDAT')
        IDAT_data = zlib.decompress(IDAT_data)
        keys = Keys(512)
        public_key = keys.create_public_key()
        private_key = keys.create_private_key()
        rsa = RSA(public_key, private_key)
        self.encrypted_data, self.addit_data = rsa.ecb_encrypt(IDAT_data)
        self.decrypted_data = rsa.ecb_decrypt(self.encrypted_data, self.addit_data)

    # self.encrypt_data_from_library, self.addit_data_from_library = rsa.crypto_library_encrypt(IDAT_data)

    def IDAT_chunk_processor_cbc(self):
        IDAT_data = b''.join(chunk.chunk_data for chunk in self.chunks
                             if chunk.chunk_type == b'IDAT')
        IDAT_data = zlib.decompress(IDAT_data)
        keys = Keys(512)
        public_key = keys.create_public_key()
        private_key = keys.create_private_key()
        rsa = RSA(public_key, private_key)
        self.encrypted_data, self.addit_data = rsa.cbc_encrypt(IDAT_data)
        self.decrypted_data = rsa.cbc_decrypt(self.encrypted_data, self.addit_data)

    def IEND_chunk_processor(self):
        chunks_number = len(self.chunks)
        if self.chunks[chunks_number - 1].chunk_type != b"IEND":
            print("IEND must be the last chunk")

    def create_new_image(self):
        filename = "tmp_image.png"
        path = "./images/{}".format(filename)
        if Path(path).is_file():
            os.remove(path)
        temp_file = open(path, 'wb')
        temp_file.write(PNGChunkProcessor.PNG_SIGNATURE)
        for chunk in self.chunks:
            if chunk.chunk_type in [b'IDAT']:
                data = zlib.compress(self.decrypted_data, 9)
                crc = zlib.crc32(data, zlib.crc32(struct.pack('>4s', b'IDAT')))
                chunk_len = len(data)
                temp_file.write(struct.pack('>I', chunk_len))
                temp_file.write(chunk.chunk_type)
                temp_file.write(data)
                temp_file.write(struct.pack('>I', crc))
            else:
                temp_file.write(struct.pack('>I', chunk.chunk_length))
                temp_file.write(chunk.chunk_type)
                temp_file.write(chunk.chunk_data)
                temp_file.write(struct.pack('>I', chunk.chunk_crc))
        temp_file.close()
        return filename

    def create_ecb_image(self):
        filename = "ecb_image.png"
        path = "./images/{}".format(filename)
        if Path(path).is_file():
            os.remove(path)
        temp_file = open(path, 'wb')
        temp_file.write(PNGChunkProcessor.PNG_SIGNATURE)
        for chunk in self.chunks:
            if chunk.chunk_type in [b'IDAT']:
                data = zlib.compress(self.encrypted_data, 9)
                crc = zlib.crc32(data, zlib.crc32(struct.pack('>4s', b'IDAT')))
                chunk_len = len(data)
                temp_file.write(struct.pack('>I', chunk_len))
                temp_file.write(chunk.chunk_type)
                temp_file.write(data)
                temp_file.write(struct.pack('>I', crc))
            else:
                temp_file.write(struct.pack('>I', chunk.chunk_length))
                temp_file.write(chunk.chunk_type)
                temp_file.write(chunk.chunk_data)
                temp_file.write(struct.pack('>I', chunk.chunk_crc))
        temp_file.close()
        return filename

    def create_cbc_image(self):
        filename = "cbc_image.png"
        path = "./images/{}".format(filename)
        if Path(path).is_file():
            os.remove(path)
        temp_file = open(path, 'wb')
        temp_file.write(PNGChunkProcessor.PNG_SIGNATURE)
        for chunk in self.chunks:
            if chunk.chunk_type in [b'IDAT']:
                data = zlib.compress(self.encrypted_data, 9)
                crc = zlib.crc32(data, zlib.crc32(struct.pack('>4s', b'IDAT')))
                chunk_len = len(data)
                temp_file.write(struct.pack('>I', chunk_len))
                temp_file.write(chunk.chunk_type)
                temp_file.write(data)
                temp_file.write(struct.pack('>I', crc))
            else:
                temp_file.write(struct.pack('>I', chunk.chunk_length))
                temp_file.write(chunk.chunk_type)
                temp_file.write(chunk.chunk_data)
                temp_file.write(struct.pack('>I', chunk.chunk_crc))
        temp_file.close()
        return filename

    def create_ecb_library_image(self):
        filename = "ecb_library_image.png"
        path = "./images/{}".format(filename)
        if Path(path).is_file():
            os.remove(path)
        temp_file = open(path, 'wb')
        temp_file.write(PNGChunkProcessor.PNG_SIGNATURE)
        for chunk in self.chunks:
            if chunk.chunk_type in [b'IDAT']:
                data = zlib.compress(self.encrypted_data_from_library, 9)
                crc = zlib.crc32(data, zlib.crc32(struct.pack('>4s', b'IDAT')))
                chunk_len = len(data)
                temp_file.write(struct.pack('>I', chunk_len))
                temp_file.write(chunk.chunk_type)
                temp_file.write(data)
                temp_file.write(struct.pack('>I', crc))
            else:
                temp_file.write(struct.pack('>I', chunk.chunk_length))
                temp_file.write(chunk.chunk_type)
                temp_file.write(chunk.chunk_data)
                temp_file.write(struct.pack('>I', chunk.chunk_crc))
        temp_file.close()
        return filename

    def create_decrypted_image_ecb(self):
        filename = "ecb_decrypted_image.png"
        path = "./images/{}".format(filename)
        if Path(path).is_file():
            os.remove(path)
        temp_file = open(path, 'wb')
        temp_file.write(PNGChunkProcessor.PNG_SIGNATURE)
        for chunk in self.chunks:
            if chunk.chunk_type in [b'IDAT']:
                data = zlib.compress(self.decrypted_data, 9)
                crc = zlib.crc32(data, zlib.crc32(struct.pack('>4s', b'IDAT')))
                chunk_len = len(data)
                temp_file.write(struct.pack('>I', chunk_len))
                temp_file.write(chunk.chunk_type)
                temp_file.write(data)
                temp_file.write(struct.pack('>I', crc))
            else:
                temp_file.write(struct.pack('>I', chunk.chunk_length))
                temp_file.write(chunk.chunk_type)
                temp_file.write(chunk.chunk_data)
                temp_file.write(struct.pack('>I', chunk.chunk_crc))
        temp_file.close()
        return filename

    def create_decrypted_image_cbc(self):
        filename = "cbc_decrypted_image.png"
        path = "./images/{}".format(filename)
        if Path(path).is_file():
            os.remove(path)
        temp_file = open(path, 'wb')
        temp_file.write(PNGChunkProcessor.PNG_SIGNATURE)
        for chunk in self.chunks:
            if chunk.chunk_type in [b'IDAT']:
                data = zlib.compress(self.decrypted_data, 9)
                crc = zlib.crc32(data, zlib.crc32(struct.pack('>4s', b'IDAT')))
                chunk_len = len(data)
                temp_file.write(struct.pack('>I', chunk_len))
                temp_file.write(chunk.chunk_type)
                temp_file.write(data)
                temp_file.write(struct.pack('>I', crc))
            else:
                temp_file.write(struct.pack('>I', chunk.chunk_length))
                temp_file.write(chunk.chunk_type)
                temp_file.write(chunk.chunk_data)
                temp_file.write(struct.pack('>I', chunk.chunk_crc))
        temp_file.close()
        return filename
