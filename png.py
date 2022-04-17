import zlib
import matplotlib.pyplot as plt
import numpy as np


class Png:
    def __init__(self, filepath):
        self.file = open(filepath, 'rb')
        self.chunks = []

    def check_signature(self):
        return self.file.read(8) == b'\x89PNG\r\n\x1a\n'  # png signature in binary

    def read_chunks(self):
        chunk_length = self.file.read(4)
        chunk_type = self.file.read(4)
        chunk_data = self.file.read(int.from_bytes(chunk_length, byteorder="big"))
        check_sum = zlib.crc32(chunk_type + chunk_data)
        chunk_crc = int.from_bytes(self.file.read(4), byteorder="big")
        if check_sum == chunk_crc:
            return chunk_type, chunk_data
        else:
            raise Exception("Not valid chunk")

    def read_all_chunks(self):
        while 1:
            chunk_type, chunk_data = self.read_chunks()
            self.chunks.append((chunk_type, chunk_data))
            if chunk_type == b'IEND':
                self.merge_chunks()
                break

    def merge_chunks(self):
        IDAT_data = b''.join(chunk_data for chunk_type, chunk_data in self.chunks if chunk_type == b'IDAT')
        self.chunks = [item for item in self.chunks if item[0] != b'IDAT']
        self.chunks.insert(-1, (b'IDAT', IDAT_data))

    # def parse_IDAT(self,chunk):


example = Png('Data/example.png')
if example.check_signature():
    example.read_all_chunks()
    print(example.chunks)
