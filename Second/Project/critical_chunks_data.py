import numpy
import matplotlib.pyplot as plt

class IHDRData:

    def __init__(self, IHDR_data_values):
        self.IHDR_data = []
        self.IHDR_data = IHDR_data_values
        self.width = self.IHDR_data[0]
        self.height = self.IHDR_data[1]
        self.bit_depth = self.IHDR_data[2]
        self.color_type = self.IHDR_data[3]
        self.compression_method = self.IHDR_data[4]
        self.filter_method = self.IHDR_data[5]
        self.interlace_method = self.IHDR_data[6]


    def get_width(self):
        return self.width


    def get_height(self):
        return self.height


    def get_color_type(self):
        return self.color_type


    def get_bit_depth(self):
        return self.bit_depth

