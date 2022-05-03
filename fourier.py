import numpy as np
from PIL import Image
from matplotlib import pyplot as plt
import math


def show_plots(path):
    fig = plt.figure(figsize=(6, 4))
    source_image = Image.open(path)
    # source_image = source_image.resize((source_image.width // 2, source_image.height // 2))
    image1 = np.array(source_image.convert('L'))
    image2 = np.fft.fft2(image1)
    image3 = np.fft.fftshift(image2)

    plt.subplot(221), plt.imshow(image1, "gray"), plt.title("Image")
    plt.subplot(222), plt.imshow(np.log(np.abs(image2)),
                                 "gray"), plt.title("Spectrum")
    plt.subplot(223), plt.imshow(np.log(np.abs(image3)),
                                 "gray"), plt.title("Centered")
    plt.subplot(224), plt.imshow(np.log(np.abs(0.001 + np.angle(image3))),
                                 "gray"), plt.title("Phase")
    plt.imshow(np.array(source_image).reshape((source_image.height, source_image.width, 4)))
    return fig
