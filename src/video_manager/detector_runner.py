# USAGE
# python src/runner/runner.py -i ~/repos/python/src/github.ibm.com/krisztian-benda/smart-caption-localization/test_images/4cars.png -o ~/repos/python/src/github.ibm.com/krisztian-benda/smart-caption-localization/src/runner/try --detectors ct -sh 130 -w 1000

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
ap.add_argument("-w", "--subtitle_width", type=int,
    help="the subtitle rectangle width in pixel")
ap.add_argument("-sh", "--subtitle_height", type=int,
    help="the subtitle rectangle height in pixel")

class ImageHandler:
    def __init__(self):
        self.images = []

    def add_image(self, image):
        self.images.append(image)
        return self

    def get_images(self):
        return self.images
        
def count_edge_ratio(area):
    return np.sum(area) / np.asarray(area).size

def main():
    args = vars(ap.parse_args())
    image_handler = ImageHandler()
    image_handler.add_image(args['image'])
    get_coordinates(image_handler, args['output_folder'], args['detectors'], args['subtitle_width'], args['subtitle_height'])

def save_rectangle(image, x, y, width, height, output_folder):
    image[y:y+height, x:x+width] = 1
    enabling_map_image = Image.fromarray(image * 255)
    enabling_map_image.save(output_folder + '/enabling_map_rectangle.tiff')

def run_canny(image_path, output_file):
    canny_command = ['python3', '~/repos/python/src/github.ibm.com/krisztian-benda/smart-caption-localization/src/canny_edge_detector/fast_detector.py',
        '--image', image_path, 
        '--output', output_file]
    p = subprocess.Popen(" ".join(canny_command), stdout=subprocess.PIPE, shell=True)
    #(output, err) = p.communicate()
    p.communicate()
    # p_status = p.wait()
    p.wait()

def run_object(image_path, output_file):
    original_cwd = os.getcwd()
    os.chdir('/Users/krisz/repos/python/src/github.ibm.com/krisztian-benda/smart-caption-localization/src/object_detector')
    object_command = ['python3', '~/repos/python/src/github.ibm.com/krisztian-benda/smart-caption-localization/src/object_detector/object-detector-subtitle-positioner.py',
        '--image', image_path,
        '--output', output_file,
        '2>/dev/null'] # Hide the unnecessary net build log
    p = subprocess.Popen(" ".join(object_command), stdout=subprocess.PIPE, shell=True)
    # (output, err) = p.communicate()
    # p_status = p.wait()
    p.communicate()
    p.wait()
    os.chdir(original_cwd)

def run_text(image_path, output_file):
    text_command = ['python3', '~/repos/python/src/github.ibm.com/krisztian-benda/smart-caption-localization/src/text_detector/text_detection.py',
        '--image', image_path,
        '--east', '~/repos/python/src/github.ibm.com/krisztian-benda/smart-caption-localization/src/text_detector/frozen_east_text_detection.pb',
        '--output', output_file,
        '-c', '0.000125']
    p = subprocess.Popen(" ".join(text_command), stdout=subprocess.PIPE, shell=True)
    # (output, err) = p.communicate()
    # p_status = p.wait()
    p.communicate()
    p.wait()

def run_logo(image_path, output_file):
    logo_command = ['python3', '~/repos/python/src/github.ibm.com/krisztian-benda/smart-caption-localization/src/logo_detector/logo-detector-subtitle-positioner.py',
        '--image', image_path,
        '--output', output_file
    ]
    p = subprocess.Popen(" ".join(logo_command), stdout=subprocess.PIPE, shell=True)
    # (output, err) = p.communicate()
    # p_status = p.wait()
    p.communicate()
    p.wait()

# runner returns with the best coordinates based on the detectors
def get_coordinates(image_handler, output_folder, detectors, subtitle_width, subtitle_height) -> (int, int):
    if os.path.isdir(output_folder):
        shutil.rmtree(output_folder)
    try:
        os.mkdir(output_folder)
    except OSError:
        print("Creation of the directory %s failed" % output_folder)
        raise
    print("Successfully created directory: %s" % output_folder)

    images = []
    image_paths = image_handler.get_images()
    for image_number in range(0, len(image_handler.get_images())):
        if 'c' in detectors:
            canny_output_file = os.path.join(output_folder, 'canny_detected_' + str(image_number) + '.tiff')
            canny_thread = Thread(target=run_canny, args=(image_paths[image_number], canny_output_file))
            canny_thread.start()
        if 'o' in detectors:  
            object_output_file = os.path.join(output_folder, 'object_detected_' + str(image_number) + '.tiff')
            object_thread = Thread(target=run_object, args=(image_paths[image_number], object_output_file))
            object_thread.start()
        if 't' in detectors:
            text_output_file = os.path.join(output_folder, 'text_detected_' + str(image_number) + '.tiff')
            text_thread = Thread(target=run_text, args=(image_paths[image_number], text_output_file))
            text_thread.start()
        if 'l' in detectors:    
            logo_output_file = os.path.join(output_folder, 'logo_detected_' + str(image_number) + '.tiff')
            logo_thread = Thread(target=run_logo, args=(image_paths[image_number], logo_output_file))
            logo_thread.start()

        if 'c' in detectors:
            canny_thread.join()
            canny_map = np.array(Image.open(canny_output_file))
            images.append(np.where(canny_map==255,1,canny_map))
        if 'o' in detectors:
            object_thread.join()
            images.append(np.array(Image.open(object_output_file)))
        if 't' in detectors:
            text_thread.join()
            images.append(np.array(Image.open(text_output_file)))
        if 'l' in detectors:
            logo_thread.join()
            images.append(np.array(Image.open(logo_output_file)))

    print("The image shape is:{}".format(images[0].shape))

    width, height = Image.open(image_paths[0]).size
    enabling_map = np.zeros((height, width))
    for image in images:
        enabling_map = enabling_map + image

    # EZT A NORAMLIZACIOT ERDEMES BELEIRNI A SZAKDOGABA
    normalized_enabling_map = (enabling_map / np.linalg.norm(enabling_map))
    enabling_map_image = Image.fromarray(normalized_enabling_map * 255)
    enabling_map_image.save(output_folder + '/enabling_map.tiff')

    swidth = int(subtitle_width)
    sheight = int(subtitle_height)
    x_step = 10
    y_step = 10
    x, y = 0, height - sheight - 1
    emap = normalized_enabling_map # for shortern name
    min_edge_ratio = 1
    min_x = int(width/2 - swidth/2) # the default place is the usual
    min_y = height - (2 * sheight)
    while y > 0:
        while x + swidth < width:
            area = emap[y:y+sheight, x:x+swidth]
            edge_ratio = count_edge_ratio(area)

            if edge_ratio < min_edge_ratio:
                min_edge_ratio = edge_ratio
                min_x = x
                min_y = y
            elif edge_ratio == min_edge_ratio:
                new_distance = np.linalg.norm(np.array([width/2,height/2]) - 
                    np.array([x + swidth/2, y+sheight/2]))
                min_area_center = np.array([min_x + swidth/2, min_y + sheight/2])
                old_distance = np.linalg.norm(np.array([width/2, height/2]) - min_area_center)
                if new_distance <= old_distance:
                    min_edge_ratio = edge_ratio
                    min_x = x
                    min_y = y


            x += x_step
        x = 0
        y -= y_step

    # print(min_x, min_y)
    save_rectangle(emap, min_x, min_y, swidth, sheight, output_folder)
    # print("THE RESULT IS: x={} and y={} pixel from the top left corner".format(min_x, min_y))
    return (min_x, min_y)

if __name__ == "__main__":
    main()
