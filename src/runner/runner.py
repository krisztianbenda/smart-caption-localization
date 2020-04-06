# USAGE
# python src/runner/runner.py -i ~/repos/python/src/github.ibm.com/krisztian-benda/smart-caption-localization/test_images/4cars.png -o ~/repos/python/src/github.ibm.com/krisztian-benda/smart-caption-localization/src/runner/try

import subprocess
import cv2
import numpy as np
import argparse
import os
import shutil
from threading import Thread
from PIL import Image
from sklearn.preprocessing import normalize

ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", type=str,
	help="path to input image")
ap.add_argument("-o", "--output_folder", type=str,
    help="path to the output folder")
ap.add_argument("-d", "--detectors", type=str, default="clot",
    help="mark here the used detector with starting letter. Like clot.")
args = vars(ap.parse_args())


if os.path.isdir(args['output_folder']):
    shutil.rmtree(args['output_folder'])
try:
    os.mkdir(args['output_folder'])
except OSError:
    print("Creation of the directory %s failed" % args['output_folder'])
    raise

print("Successfully created the directory %s " % args['output_folder'])

def run_canny():
    canny_command = ['python', '~/repos/python/src/github.ibm.com/krisztian-benda/smart-caption-localization/src/canny_edge_detector/fast_detector.py',
        '--image', args["image"], 
        '--output', args["output_folder"] + '/canny_detected.tiff']
    p = subprocess.Popen(" ".join(canny_command), stdout=subprocess.PIPE, shell=True)
    (output, err) = p.communicate()
    p_status = p.wait()

def run_object():
    os.chdir('/Users/krisz/repos/python/src/github.ibm.com/krisztian-benda/smart-caption-localization/src/object_detector')
    object_command = ['python', '~/repos/python/src/github.ibm.com/krisztian-benda/smart-caption-localization/src/object_detector/object-detector-subtitle-positioner.py',
        '--image', args["image"],
        '--output', args["output_folder"] + '/object_detected.tiff']
    p = subprocess.Popen(" ".join(object_command), stdout=subprocess.PIPE, shell=True)
    (output, err) = p.communicate()
    p_status = p.wait()

def run_text():
    text_command = ['python', '~/repos/python/src/github.ibm.com/krisztian-benda/smart-caption-localization/src/text_detector/text_detection.py',
        '--image', args["image"],
        '--east', '~/repos/python/src/github.ibm.com/krisztian-benda/smart-caption-localization/src/text_detector/frozen_east_text_detection.pb',
        '--output', args["output_folder"] + '/text_detected.tiff',
        '-c', '0.000125']
    p = subprocess.Popen(" ".join(text_command), stdout=subprocess.PIPE, shell=True)
    (output, err) = p.communicate()
    p_status = p.wait()

def run_logo():
    logo_command = ['python', '~/repos/python/src/github.ibm.com/krisztian-benda/smart-caption-localization/src/logo_detector/logo-detector-subtitle-positioner.py',
        '--image', args["image"],
        '--output', args["output_folder"] + '/logo_detected.tiff'
    ]
    p = subprocess.Popen(" ".join(logo_command), stdout=subprocess.PIPE, shell=True)
    (output, err) = p.communicate()
    p_status = p.wait()


canny_thread = Thread(target=run_canny)
object_thread = Thread(target=run_object)
text_thread = Thread(target=run_text)
logo_thread = Thread(target=run_logo)

if 'c' in args["detectors"]:
    canny_thread.start()
if 'o' in args["detectors"]:    
    object_thread.start()
if 't' in args["detectors"]:
    text_thread.start()
if 'l' in args["detectors"]:    
    logo_thread.start()

images = []
if 'c' in args["detectors"]:
    canny_thread.join()
    canny_map = np.array(Image.open(args["output_folder"] + '/canny_detected.tiff'))
    images.append(np.where(canny_map==255,1,canny_map))
if 'o' in args["detectors"]:
    object_thread.join()
    images.append(np.array(Image.open(args["output_folder"] + '/object_detected.tiff')))
if 't' in args["detectors"]:
    text_thread.join()
    images.append(np.array(Image.open(args["output_folder"] + '/text_detected.tiff')))
if 'l' in args["detectors"]:
    logo_thread.join()
    images.append(np.array(Image.open(args["output_folder"] + '/logo_detected.tiff')))

width, height = Image.open(args['image']).size
print(images[1].shape)
print(images[1][160][60])
print(images[1][1][1])

print(images[0].shape)
print(images[0][23][41]) # white
print(images[0][1][1]) # black

enabling_map = np.zeros((height, width))
for image in images:
    enabling_map = enabling_map + image

norm1 = (enabling_map / np.linalg.norm(enabling_map)) * 255
enabling_map_image = Image.fromarray(norm1)
enabling_map_image.save(args["output_folder"] + '/enabling_map.tiff')