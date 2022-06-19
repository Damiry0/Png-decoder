import binascii
import struct
import zlib
import matplotlib.pyplot as plt
import matplotlib.image as img
import numpy as np
import xml.dom.minidom as xdm
import rsa as rsa_alg


class Png:
    LENGTH_OF_BYTES = 4
    STEP = 0
    PNG_SIGNATURE = b'\x89PNG\r\n\x1a\n'

    def __init__(self, filepath):
        self.file = open(filepath, 'rb')
        self.chunks = []
        self.width = []
        self.height = []
        self.original_idat = []
        self.output_image = []

    def check_signature(self):
        return self.file.read(8) == self.PNG_SIGNATURE  # png signature in binary

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
        return [row[0] for row in self.chunks]

    def merge_idat_chunks(self):
        IDAT_data = b''.join(chunk_data for chunk_type, chunk_data in self.chunks if chunk_type == b'IDAT')
        self.original_idat = IDAT_data
        IDAT_data = zlib.decompress(IDAT_data)
        self.chunks = [item for item in self.chunks if item[0] != b'IDAT']
        self.chunks.insert(-1, (b'IDAT', IDAT_data))

    def parse_IHDR(self):
        if self.chunks[0][0] == b'IHDR':
            width = int.from_bytes(self.chunks[0][1][:4], byteorder="big")
            self.width = width
            height = int.from_bytes(self.chunks[0][1][4:8], byteorder="big")
            self.height = height
            bit_depth = self.chunks[0][1][8] if self.chunks[0][1][8] in (1, 2, 4, 8, 16) else Exception(
                "Not valid bit depth:" + str(self.chunks[0][1][8]))
            color_type = self.chunks[0][1][9] if self.chunks[0][1][9] in (0, 2, 3, 4, 6) else Exception(
                "Not valid Color Type" + str(self.chunks[0][1][9]))
            compression_method = self.chunks[0][1][10]
            filter_method = self.chunks[0][1][11]
            interlace_method = self.chunks[0][1][12]
            return width, height, bit_depth, color_type, compression_method, filter_method, interlace_method
        else:
            raise Exception("IHDR should be the first chunk")

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
        for r in range(height):
            filter_type = idat_chunk[i]
            i += 1
            for c in range(self.STEP):
                Filter = idat_chunk[i]
                i += 1
                if filter_type == 0:
                    Recon_x = Filter
                elif filter_type == 1:
                    Recon_x = Filter + self.unfilter_sub(r, c)
                elif filter_type == 2:
                    Recon_x = Filter + self.unfilter_up(r, c)
                elif filter_type == 3:
                    Recon_x = Filter + (self.unfilter_sub(r, c) + self.unfilter_up(r, c)) // 2
                elif filter_type == 4:
                    Recon_x = Filter + self.paeth_predictor(self.unfilter_sub(r, c), self.unfilter_up(r, c),
                                                            self.unfilter_average(r, c))
                else:
                    return self.output_image
                self.output_image.append(Recon_x & 0xff)  # truncation to byte
        return self.output_image

    def parse_IDAT_ecb(self, image, height, width):
        i = 0
        idat_chunk = image
        self.STEP = self.LENGTH_OF_BYTES * width
        for r in range(height):
            filter_type = idat_chunk[i]
            i += 1
            for c in range(self.STEP):
                Filter = idat_chunk[i]
                i += 1
                if filter_type == 0:
                    Recon_x = Filter
                elif filter_type == 1:
                    Recon_x = Filter + self.unfilter_sub(r, c)
                elif filter_type == 2:
                    Recon_x = Filter + self.unfilter_up(r, c)
                elif filter_type == 3:
                    Recon_x = Filter + (self.unfilter_sub(r, c) + self.unfilter_up(r, c)) // 2
                elif filter_type == 4:
                    Recon_x = Filter + self.paeth_predictor(self.unfilter_sub(r, c), self.unfilter_up(r, c),
                                                            self.unfilter_average(r, c))
                else:
                    return self.output_image
                self.output_image.append(Recon_x & 0xff)  # truncation to byte
        return self.output_image

    def parse_PLTE(self):
        plte_palette = []
        for chunk in self.chunks:
            if chunk[0] == b'PLTE':
                plte_len = len(chunk[1])
                if plte_len % 3 != 0:
                    raise Exception("PLTE chunk length must be divisible by 3.")
                for i in range(0, plte_len, 3):
                    pixel = chunk[1][i:i + 3]
                    plte_palette.append((pixel[0], pixel[1], pixel[2]))
                palette = np.array(plte_palette)
                index = np.arange(256).reshape(16, 16)
                fig = plt.figure()
                plt.title("PLTE palette")
                plt.imshow(palette[index])
                return fig

    def parse_gAMA(self):
        gamma = "Unknown"
        for chnk in self.chunks:
            if chnk[0] == b'gAMA':
                g = int.from_bytes(chnk[1], "big")
                gamma = str(g / 100000)
        return gamma

    def parse_cHRM(self):
        chrm = "Unknown"
        for chnk in self.chunks:
            if chnk[0] == b'cHRM':
                chrm = [('WP X:', int.from_bytes(chnk[1][:4], "big")),
                        ('WP Y:', int.from_bytes(chnk[1][4:8], "big")),
                        ("Red X:", int.from_bytes(chnk[1][8:12], "big")),
                        ("Red Y:", int.from_bytes(chnk[1][12:16], "big")),
                        ("Green X:", int.from_bytes(chnk[1][12:16], "big")),
                        ("Green Y:", int.from_bytes(chnk[1][12:16], "big")),
                        ("Blue X:", int.from_bytes(chnk[1][12:16], "big")),
                        ("Blue Y:", int.from_bytes(chnk[1][12:16], "big"))]
        return chrm

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
                if (unit_b):
                    unit = "meter"
                else:
                    unit = "unknown"
                return int.from_bytes(ppuX, "big"), int.from_bytes(ppuY, "big"), unit
        return phys

    def parse_tIME(self):
        time = "Unknown"
        for chnk in self.chunks:
            if chnk[0] == b'tIME':
                month = int.from_bytes(chnk[1][2:3], "big")
                if month < 10:
                    month = "0" + str(month)
                time = f'Date:{int.from_bytes(chnk[1][3:4], "big")}.{month}.{int.from_bytes(chnk[1][:2], "big")} ' \
                       f'Time:{int.from_bytes(chnk[1][4:5], "big")}:{int.from_bytes(chnk[1][5:6], "big")}:{int.from_bytes(chnk[1][6:7], "big")}'
        return time

    def parse_tEXt(self):
        text = "Unknown"
        data = []
        list_data = []
        key = []
        value = []
        word = ""
        checker = True
        for chnk in self.chunks:
            if chnk[0] == b'tEXt':
                data += chnk
        if data is not None:
            text = data
            for item in data:
                if item == b'tEXt':
                    data.remove(item)
            for i in data:
                print(i)
            for item in data:
                for letter in item:
                    if chr(letter) is chr(0):
                        list_data.append(word)
                        word = ""
                    else:
                        word += chr(letter)
                list_data.append(word)
                word = ""
            for item in list_data:
                if checker:
                    key.append(item)
                    checker = False
                else:
                    value.append(item)
                    checker = True
            text_dict = dict(zip(key, value))
        return text_dict

    def parse_iTXt(self):
        text = "Unknown"
        data = []
        list_data = []
        key = []
        value = []
        word = ""
        checker = True
        for chnk in self.chunks:
            if chnk[0] == b'iTXt':
                data += chnk
        if data is not None:
            text = data
            for item in data:
                if item == b'iTXt':
                    data.remove(item)
            for item in data:
                s = str(item)
                if s.startswith("b'XML:com.adobe.xmp"):
                    s = s.removeprefix("b'XML:com.adobe.xmp")
                    if s.startswith("\\x00\\x00\\x00\\x00\\x00"):
                        s = s[20:-1]
                    print("XD", s)
                    dom = xdm.parseString(s)
                    prett = dom.toprettyxml()
                    text_dict = prett
                    return text_dict
                else:
                    for letter in item:
                        if chr(letter) is chr(0):
                            list_data.append(word)
                            word = ""
                        else:
                            word += chr(letter)
                    list_data.append(word)
                    word = ""
            for item in list_data:
                if checker:
                    key.append(item)
                    checker = False
                else:
                    value.append(item)
                    checker = True
            text_dict = dict(zip(key, value))
            return text_dict

    def anonymization(self):
        chunks = [(x, y) for x, y in self.chunks if x.decode()[0].isupper()]
        decoded_chunks = []
        for (chunk_name, chunk_data) in chunks:
            chunk_length = len(chunk_data).to_bytes(4, byteorder='big').hex()
            check_sum = zlib.crc32(chunk_name + chunk_data).to_bytes(4, byteorder='big').hex()
            if chunk_name == b'IDAT':
                chunk_data = self.original_idat
            decoded_chunks = decoded_chunks + [chunk_length] + [chunk_name.hex()] + [chunk_data.hex()] + [check_sum]
        decoded_chunks = [self.PNG_SIGNATURE.hex()] + decoded_chunks
        decoded_chunks = ''.join(map(str, decoded_chunks))
        decoded_chunks = binascii.unhexlify(decoded_chunks)
        return decoded_chunks

    def create_ecb_image(self, encrypt_data):
        filename = "ecb_haha.png"
        temporary_file = open(filename, 'wb')
        temporary_file.write(self.PNG_SIGNATURE)
        for (chunk_name, chunk_data) in self.chunks:
            if chunk_name in [b'IDAT']:
                new_data = zlib.compress(encrypt_data, 9)
                new_crc = zlib.crc32(new_data, zlib.crc32(struct.pack('>4s', b'IDAT')))
                chunk_len = len(new_data)
                temporary_file.write(struct.pack('>I', chunk_len))
                temporary_file.write(chunk_name)
                temporary_file.write(new_data)
                temporary_file.write(struct.pack('>I', new_crc))
            else:
                chunk_len = len(chunk_data)
                check_sum = zlib.crc32(chunk_data, zlib.crc32(struct.pack('>4s', chunk_name)))
                temporary_file.write(struct.pack('>I', chunk_len))
                temporary_file.write(chunk_name)
                temporary_file.write(chunk_name)
                temporary_file.write(struct.pack('>I', check_sum))
        temporary_file.close()
        return filename

    def IDAT_chunk_processor_ecb(self):
        decrypt_data = bytearray()
        encrypt_data = bytearray()
        for chunk in self.chunks:
            if chunk[0] == b'IDAT':
                rsa = rsa_alg.RSA(128)
                encrypt_data = rsa.encrypt_ecb(chunk[1])
                encrypt_data_processed = self.parse_IDAT_ecb(encrypt_data, self.height, self.width)
                decrypt_data = rsa.decrypt_ecb(encrypt_data)
                print(1)
        return encrypt_data_processed

    def save_file(self, file_name, encrypted_data):
        filename = f"{file_name}.png"
        file_ = open(filename, 'wb')
        file_.write(self.PNG_SIGNATURE)
        for chunk_type, chunk_data in self.chunks:
            if chunk_type in [b'IDAT']:
                idat_data = bytes(encrypted_data)
                new_data, new_crc = self.compress_IDAT(idat_data)
                chunk_len = len(new_data)
                file_.write(struct.pack('>I', chunk_len))
                file_.write(chunk_type)
                file_.write(new_data)
                file_.write(struct.pack('>I', new_crc))
            else:
                chunk_len = len(chunk_data)
                check_sum = zlib.crc32(chunk_type + chunk_data)
                file_.write(struct.pack('>I', chunk_len))
                file_.write(chunk_type)
                file_.write(chunk_data)
                file_.write(struct.pack('>I', check_sum))
        file_.close()
        return filename

    def compress_IDAT(self, all_data):
        new_data = zlib.compress(all_data, 9)
        crc = zlib.crc32(new_data, zlib.crc32(struct.pack('>4s', b'IDAT')))
        return new_data, crc


def open_png(filepath):
    example = Png(filepath)
    if example.check_signature():
        chunk_names = example.read_all_chunks()
        Width, Height, Bit_depth, Color_type, Compression_method, Filter_method, Interlace_method = example.parse_IHDR()
        image = example.parse_IDAT(Height, Width)
        PLTE = example.parse_PLTE()
        Gamma = example.parse_gAMA()
        SRGB = example.parse_sRGB()
        PHYs = example.parse_pHYs()
        CHRM = example.parse_cHRM()
        TIME = example.parse_tIME()
        TEXT = example.parse_tEXt()
        ITXT = example.parse_iTXt()
        # ITXT = yaml.dump(xmltodict.parse(ITXT), default_flow_style=False)
        anomizated_chunks = example.anonymization()
    else:
        raise Exception("Wrong Filetype")
    fig = plt.figure()
    image = img.imread(filepath)
    plt.imshow(image)
    return fig, chunk_names, Width, Height, Bit_depth, Color_type, Gamma, SRGB, PHYs, CHRM, TIME, TEXT, ITXT, Compression_method, Filter_method, Interlace_method, anomizated_chunks, PLTE
