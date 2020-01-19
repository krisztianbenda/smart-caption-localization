# source: https://github.com/FienSoP/canny_edge_detector

import canny_edge_detector as ced
import numpy as np
from PIL import Image
import math, copy, cv2
import argparse
import numpy as np
import skimage
import matplotlib.pyplot as plt 
import matplotlib.image as mpimg
import os
import scipy.misc as sm

ap = argparse.ArgumentParser()
ap.add_argument('-i', '--image', required=True, help='path to input image')

def rgb2gray(rgb):
    r, g, b = rgb[:,:,0], rgb[:,:,1], rgb[:,:,2]
    gray = 0.2989 * r + 0.5870 * g + 0.1140 * b
    return gray

def load_data(filename):    
    '''
    Load images from the "faces_imgs" directory
    Images are in JPG and we convert it to gray scale images
    '''
    img = None
    if os.path.isfile(filename):
        img = mpimg.imread(filename)
        img = rgb2gray(img)
    else:
        print('The input file is not an image or not exits')
    return img


def visualize(img, format=None, gray=False):
    if img.shape[0] == 3:
        img = img.transpose(1,2,0)

    fig = plt.figure(frameon=False)
    fig.set_size_inches(img.shape[1]/100,img.shape[0]/100)
    ax = plt.Axes(fig, [0., 0., 1., 1.])
    ax.set_axis_off()
    fig.add_axes(ax)

    ax.imshow(img, format, aspect='auto')
    fig.savefig('./src/detection_results/canny_edge.png')


def main():
    args = ap.parse_args()
    img = load_data(args.image)

    detector = ced.cannyEdgeDetector(img, sigma=1.4, kernel_size=5,
        lowthreshold=0.01, highthreshold=0.1, weak_pixel=100)

    detected = detector.detect()
    visualize(detected, 'gray')


if __name__ == '__main__':
    main()