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
        self.encrypt_data = bytearray()
        self.after_iend_data = bytearray()
        self.decrypt_data = bytearray()
        self.encrypt_data_from_library = bytearray()
        self.after_iend_data__from_library = bytearray()


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
        public_key = keys.create_publc_key()
        private_key = keys.create_private_key()
        rsa = RSA(public_key, private_key)
        self.encrypt_data, self.after_iend_data = rsa.ecb_encrypt(IDAT_data)
        self.decrypt_data = rsa.ecb_decrypt(self.encrypt_data, self.after_iend_data)
        # self.encrypt_data_from_library, self.after_iend_data__from_library = rsa.crypto_library_encrypt(IDAT_data)

    def IDAT_chunk_processor_cbc(self):
        IDAT_data = b''.join(chunk.chunk_data for chunk in self.chunks
                                            if chunk.chunk_type == b'IDAT')
        IDAT_data = zlib.decompress(IDAT_data)
        keys = Keys(512)
        public_key = keys.create_publc_key()
        private_key = keys.create_private_key()
        rsa = RSA(public_key, private_key)
        self.encrypt_data, self.after_iend_data = rsa.cbc_encrypt(IDAT_data)
        self.decrypt_data = rsa.cbc_decrypt(self.encrypt_data, self.after_iend_data)

    def IEND_chunk_processor(self):
        number_of_chunks = len(self.chunks)
        if self.chunks[number_of_chunks-1].chunk_type != b"IEND":
            print("IEND must be the last chunk")
        IEND_data = struct.unpack('>', self.chunks[number_of_chunks - 1].chunk_data)

    def create_new_image(self):
        filename = "tmp.png"
        img_path = "./images/{}".format(filename)
        if Path(img_path).is_file():
            os.remove(img_path)
        temporary_file = open(img_path, 'wb')
        temporary_file.write(PNGChunkProcessor.PNG_SIGNATURE)
        for chunk in self.chunks:
            if chunk.chunk_type in [b'IDAT']:
                new_data = zlib.compress(self.decrypt_data, 9)
                new_crc = zlib.crc32(new_data, zlib.crc32(struct.pack('>4s', b'IDAT')))
                chunk_len = len(new_data)
                temporary_file.write(struct.pack('>I', chunk_len))
                temporary_file.write(chunk.chunk_type)
                temporary_file.write(new_data)
                temporary_file.write(struct.pack('>I', new_crc))
            else:
                temporary_file.write(struct.pack('>I', chunk.chunk_length))
                temporary_file.write(chunk.chunk_type)
                temporary_file.write(chunk.chunk_data)
                temporary_file.write(struct.pack('>I', chunk.chunk_crc))
        temporary_file.close()
        return filename

    def create_ecb_image(self):
        filename = "ecb.png"
        img_path = "./images/{}".format(filename)
        if Path(img_path).is_file():
            os.remove(img_path)
        temporary_file = open(img_path, 'wb')
        temporary_file.write(PNGChunkProcessor.PNG_SIGNATURE)
        for chunk in self.chunks:
            if chunk.chunk_type in [b'IDAT']:
                new_data = zlib.compress(self.encrypt_data, 9)
                new_crc = zlib.crc32(new_data, zlib.crc32(struct.pack('>4s', b'IDAT')))
                chunk_len = len(new_data)
                temporary_file.write(struct.pack('>I', chunk_len))
                temporary_file.write(chunk.chunk_type)
                temporary_file.write(new_data)
                temporary_file.write(struct.pack('>I', new_crc))
            else:
                temporary_file.write(struct.pack('>I', chunk.chunk_length))
                temporary_file.write(chunk.chunk_type)
                temporary_file.write(chunk.chunk_data)
                temporary_file.write(struct.pack('>I', chunk.chunk_crc))
        temporary_file.close()
        return filename

    def create_cbc_image(self):
        filename = "cbc.png"
        img_path = "./images/{}".format(filename)
        if Path(img_path).is_file():
            os.remove(img_path)
        temporary_file = open(img_path, 'wb')
        temporary_file.write(PNGChunkProcessor.PNG_SIGNATURE)
        for chunk in self.chunks:
            if chunk.chunk_type in [b'IDAT']:
                new_data = zlib.compress(self.encrypt_data, 9)
                new_crc = zlib.crc32(new_data, zlib.crc32(struct.pack('>4s', b'IDAT')))
                chunk_len = len(new_data)
                temporary_file.write(struct.pack('>I', chunk_len))
                temporary_file.write(chunk.chunk_type)
                temporary_file.write(new_data)
                temporary_file.write(struct.pack('>I', new_crc))
            else:
                temporary_file.write(struct.pack('>I', chunk.chunk_length))
                temporary_file.write(chunk.chunk_type)
                temporary_file.write(chunk.chunk_data)
                temporary_file.write(struct.pack('>I', chunk.chunk_crc))
        temporary_file.close()
        return filename

    '''def create_ecb_library_image(self):
        filename = "ecb_library.png"
        img_path = "./images/{}".format(filename)
        if Path(img_path).is_file():
            os.remove(img_path)
        temporary_file = open(img_path, 'wb')
        temporary_file.write(PNGChunkProcessor.PNG_SIGNATURE)
        for chunk in self.chunks:
            if chunk.chunk_type in [b'IDAT']:
                new_data = zlib.compress(self.encrypt_data_from_library, 9)
                new_crc = zlib.crc32(new_data, zlib.crc32(struct.pack('>4s', b'IDAT')))
                chunk_len = len(new_data)
                temporary_file.write(struct.pack('>I', chunk_len))
                temporary_file.write(chunk.chunk_type)
                temporary_file.write(new_data)
                temporary_file.write(struct.pack('>I', new_crc))
            else:
                temporary_file.write(struct.pack('>I', chunk.chunk_length))
                temporary_file.write(chunk.chunk_type)
                temporary_file.write(chunk.chunk_data)
                temporary_file.write(struct.pack('>I', chunk.chunk_crc))
        temporary_file.close()
        return filename'''
