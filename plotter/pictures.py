
import logging

import matplotlib.pyplot as plt
import numpy as np

import pandas as pd
import seaborn as sns
from PIL import  Image
from PIL import ImageEnhance


logging.basicConfig(format='%(asctime)s %(levelname)s %(name)s: %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__file__)

class Adjustment:

    def __init__(self):
        logger.debug("Adjustment created")


    def adjust_brigthness(self, input_image, output_image, factor):
        image = Image.open(input_image)
        enhancer_object = ImageEnhance.Brightness(image)
        out = enhancer_object.enhance(factor)
        out.save(output_image)

    def adjust_sharpness(self, input_image, output_image, factor):
        image = Image.open(input_image)
        enhancer_object = ImageEnhance.Sharpness(image)
        out = enhancer_object.enhance(factor)
        out.save(output_image)

    def adjust_contrast(self, input_image, output_image, factor):
        image = Image.open(input_image)
        enhancer_object = ImageEnhance.Contrast(image)
        out = enhancer_object.enhance(factor)
        out.save(output_image)


def main():

    adj = Adjustment()
    input_path = "fig50.png"
    output_path = "fig50_output.png"
    output_path_2 = "fig50_output_2.png"
    adj.adjust_contrast(input_path, output_path, 1)
    adj.adjust_sharpness(output_path, output_path_2,3)
    #adj.adjust_contrast(output_path, output_path_2,1.7)




if __name__ == '__main__':
    main()
