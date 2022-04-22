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
    x        IDAT_data = zlib.decompress(IDAT_data)
        self.chunks = [item for item in self.chunks if item[0] != b'IDAT']
        self.chunks.insert(-1, (b'IDAT', IDAT_data))

    def parse_IHDR(self):
        if self.chunks[0][0] == b'IHDR':
            Width = int.from_bytes(self.chunks[0][1][:4], byteorder="big")
            Height = int.from_bytes(self.chunks[0][1][4:8], byteorder="big")
            Bit_depth = self.chunks[0][1][8]
            Color_type = self.chunks[0][1][9]
            Compression_method = self.chunks[0][1][10]
            Filter_method = self.chunks[0][1][11]
            Interlace_method = self.chunks[0][1][12]
            return Width, Height, Bit_depth, Color_type, Compression_method, Filter_method, Interlace_method
        else:
            raise Exception("IHDR should be the second chunk")

    def parse_PLTE(self, chunk):
        red = chunk[1][0]
        green = chunk[1][0]
        blue = chunk[1][2]
        return red, green, blue

    def paeth_predictor(a, b, c):
        p = a + b - c  # a= left, b= above, c= right
        pa = abs(p - a)
        pb = abs(p - b)
        pc = abs(p - c)
        # return nearest of a,b,c
        # breaking ties in order a,b,c
        if pa <= pb and pa <= pc:
            return a
        elif pb <= pc:
            return b
        else:
            return c

    # def unfilter_sub(self):
    #     return
    # def unfilter_up(self):
    #     return
    # def unfilter_average(self):
    #     return
    # def unfilter_paeth(self):
    #     return


def parse_IDAT(self,chunk):
        output_image=[]
        filter_type=chunk[]




example = Png('Data/example.png')
if example.check_signature():
    example.read_all_chunks()
    Width, Height, Bit_depth, Color_type, Compression_method, Filter_method, Interlace_method = example.parse_IHDR()
    print(1)
