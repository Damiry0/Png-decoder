import zlib
import matplotlib.pyplot as plt
import numpy as np


class Png:
    LENGTH_OF_BYTES = 4
    STEP = 0

    def __init__(self, filepath):
        self.file = open(filepath, 'rb')
        self.chunks = []
        self.output_image = []

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
                self.merge_idat_chunks()
                break

    def merge_idat_chunks(self):
        IDAT_data = b''.join(chunk_data for chunk_type, chunk_data in self.chunks if chunk_type == b'IDAT')
        IDAT_data = zlib.decompress(IDAT_data)
        self.chunks = [item for item in self.chunks if item[0] != b'IDAT']
        self.chunks.insert(-1, (b'IDAT', IDAT_data))

    def parse_IHDR(self):
        if self.chunks[0][0] == b'IHDR':
            width = int.from_bytes(self.chunks[0][1][:4], byteorder="big")
            height = int.from_bytes(self.chunks[0][1][4:8], byteorder="big")
            bit_depth = self.chunks[0][1][8] if self.chunks[0][1][8] in (1, 2, 4, 8, 16) else Exception(
                "Not valid bit depth:" + str(self.chunks[0][1][8]))
            color_type = self.chunks[0][1][9] if self.chunks[0][1][9] in (0, 2, 3, 4, 6) else Exception(
                "Not valid Color Type" + str(self.chunks[0][1][9]))
            compression_method = self.chunks[0][1][10]
            filter_method = self.chunks[0][1][11]
            interlace_method = self.chunks[0][1][12]
            return width, height, bit_depth, color_type, compression_method, filter_method, interlace_method
        else:
            raise Exception("IHDR should be the second chunk")

    # def parse_PLTE(self, chunk):
    #     red = chunk[1][0]
    #     green = chunk[1][0]
    #     blue = chunk[1][2]
    #     return red, green, blue

    def paeth_predictor(self, a, b, c):
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

    def unfilter_sub(self, r, c):
        return self.output_image[r * self.STEP + c - self.LENGTH_OF_BYTES] if c >= self.LENGTH_OF_BYTES else 0

    def unfilter_up(self, r, c):
        return self.output_image[(r - 1) * self.STEP + c] if r > 0 else 0

    def unfilter_average(self, r, c):
        return self.output_image[
            (r - 1) * self.STEP + c - self.LENGTH_OF_BYTES] if r > 0 and c >= self.LENGTH_OF_BYTES else 0

    def parse_IDAT(self, height, width):
        i = 0
        idat_chunk = [(x, y) for x, y in self.chunks if x == b"IDAT"][0][1]
        self.STEP = self.LENGTH_OF_BYTES * width
        for j in range(height):
            filter_type = idat_chunk[i]
            i += 1
            for k in range(self.STEP):
                Filter = idat_chunk[i]
                i += 1
                if filter_type == 0:
                    Recon_x = Filter
                elif filter_type == 1:
                    Recon_x = Filter + self.unfilter_sub(j, k)
                elif filter_type == 2:
                    Recon_x = Filter + self.unfilter_up(j, k)
                elif filter_type == 3:
                    Recon_x = Filter + (self.unfilter_sub(j, k) + self.unfilter_up(j, k)) // 2
                elif filter_type == 4:
                    Recon_x = Filter + self.paeth_predictor(self.unfilter_sub(j, k), self.unfilter_up(j, k),
                                                            self.unfilter_average(j, k))
                else:
                    raise Exception('unknown filter type: ' + str(filter_type))
                self.output_image.append(Recon_x & 0xff)  # truncation to byte
        return self.output_image

    def parse_gAMA(self):
        gamma = "Unknown"
        for chnk in self.chunks:
            if chnk[0] == b'gAMA':
                gamma = "XD"
        return gamma

    def parse_sRGB(self):
        rgb = "Unknown"
        for chnk in self.chunks:
            if chnk[0] == b'sRGB':
                rendering_indent = chnk[1]
                return {
                    b'\x00': "0: Perceptual",
                    b'\x01': "1: Relative colorimetric",
                    b'\x02': "2: Saturation",
                    b'\x03': "Absolute colorimetric",
                }[rendering_indent]
        return rgb

    def parse_pHYs(self):
        phys = "Unknown"
        for chnk in self.chunks:
            if chnk[0] == b'pHYs':
                phys = "XD"
                ppuX = chnk[1][:4]
                ppuY = chnk[1][4:8]
                unit_b = chnk[1][-1:]
                if(unit_b):
                    unit = "meter"
                else:
                    unit = "unknown"
                return int.from_bytes(ppuX, "big"), int.from_bytes(ppuY, "big"), unit
        return phys

def open_png(filepath):
    example = Png(filepath)
    if example.check_signature():
        example.read_all_chunks()
        Width, Height, Bit_depth, Color_type, Compression_method, Filter_method, Interlace_method = example.parse_IHDR()
        image = example.parse_IDAT(Height, Width)
        Gamma = example.parse_gAMA()
        SRGB = example.parse_sRGB()
        PHYs = example.parse_pHYs()
    else:
        raise Exception("Wrong Filetype")
    fig = plt.figure()
    plt.imshow(np.array(image).reshape((Height, Width, 4)))
    return fig, Width, Height, Bit_depth, Color_type, Gamma, SRGB, PHYs, Compression_method, Filter_method, Interlace_method
