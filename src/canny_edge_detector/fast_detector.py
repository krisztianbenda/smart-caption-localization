# python src/canny_edge_detector/fast_detector.py --image ~/repos/python/src/github.ibm.com/krisztian-benda/smart-caption-localization/test_images/4cars800px.png -o ./src/detection_results/canny_detected.tiff

import subprocess
import cv2
import argparse
import matplotlib.pyplot as plt
from PIL import Image

ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", type=str,
	help="path to input image")
ap.add_argument("-o", "--output", type=str,
	help="path to output image")
args = vars(ap.parse_args())

processing_image = args["image"]
img = cv2.imread(processing_image)

edges = cv2.Canny(img, 100, 200, 3, L2gradient=True)
# plt.imsave(args["output"], edges, cmap='gray', format='tiff')
enabling_map_image = Image.fromarray(edges)
enabling_map_image.save(args["output"])
