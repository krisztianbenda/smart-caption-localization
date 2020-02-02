import subprocess
import cv2
import numpy as np
import argparse
from PIL import Image

ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", type=str,
	help="path to input image")
args = vars(ap.parse_args())

processing_image = args["image"]
cmd = [
        '/Users/krisz/repos/python/src/github.ibm.com/krisztian-benda/smart-caption-localization/src/object_detector/darknet', 
        'detect', 
        '/Users/krisz/repos/python/src/github.ibm.com/krisztian-benda/smart-caption-localization/src/object_detector/cfg/yolov3.cfg',
        '/Users/krisz/repos/python/src/github.ibm.com/krisztian-benda/smart-caption-localization/src/object_detector/yolov3.weights',
        processing_image
    ]

def execute(cmd):
    popen = subprocess.Popen(cmd, stdout=subprocess.PIPE, universal_newlines=True)
    for stdout_line in iter(popen.stdout.readline, ""):
        yield stdout_line 
    popen.stdout.close()
    return_code = popen.wait()
    if return_code:
        raise subprocess.CalledProcessError(return_code, cmd)


isImportant = False
detected_objects = {}
for path in execute(cmd):    
    if "Predicted" in path:
        isImportant = True
        continue

    if isImportant:
        if "Bounding Box" not in path:
            detected_object = path.split(":")[0]
            print("An object found: ", detected_object)
            if detected_object not in detected_objects:
                detected_objects[detected_object] = []
        else:
            coord = {}
            coord['left'] = int(path.split("Left=")[1].split(",")[0])
            coord['top'] = int(path.split("Top=")[1].split(",")[0])
            coord['right'] = int(path.split("Right=")[1].split(",")[0])
            coord['bottom'] = int(path.split("Bottom=")[1].split(",")[0].split('\n')[0])
            print("bounding boxot talalatam", coord)
            print(detected_objects)
            detected_objects[detected_object].append(coord)
                

print(detected_objects)
important_objects = ['person']


img = cv2.imread(processing_image, 0)
print(img.shape)
enabling_map = np.zeros(img.shape)
for obj in detected_objects:
    for n in range(len(detected_objects[obj])):
        for x in range(detected_objects[obj][n]['left'], detected_objects[obj][n]['right']):
            for y in range(detected_objects[obj][n]['top'], detected_objects[obj][n]['bottom']):
                if obj in important_objects:
                    enabling_map[y,x] = 1
                else:
                    if enabling_map[y,x] == 0:
                        enabling_map[y,x] = 0.5

enabling_map_image = Image.fromarray(enabling_map)
enabling_map_image.save("../detection_results/object_detected.tiff")
