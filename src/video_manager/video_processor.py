import cv2
import os
import subprocess
import shutil
from detector_runner import get_coordinates
from srt_processing import SRTHandler
import pysubs2
import argparse
import math

ap = argparse.ArgumentParser()
ap.add_argument("-is", "--input_srt", type=str,
	help="path to input srt")
ap.add_argument("-iv", "--input_video", type=str,
	help="path to input video (mp4)")
ap.add_argument("-o", "--output_ass", type=str,
	help="path to the output")
args = vars(ap.parse_args()) 

srt_handler = SRTHandler(args['input_srt'])
subtitle = pysubs2.load(args['input_srt'])

vidcap = cv2.VideoCapture(args['input_video'])
width = vidcap.get(cv2.CAP_PROP_FRAME_WIDTH)
height = vidcap.get(cv2.CAP_PROP_FRAME_HEIGHT)
print("The input audio has width:%d and height:%d" % (width, height))

subtitle.info['PlayResX'] = width
subtitle.info['PlayResY'] = height
''' 
Default font size calculated from the (1920x1080) diagonal and 65 fontsize's rate
  sqrt(1920^2 + 1080^2) / 65 = input_diagonal / default_size
'''

default_fontsize = math.sqrt(width ** 2 + height ** 2) / (math.sqrt(1920 ** 2 + 1080 ** 2) / 65)
print("Default fontsize will be: {}".format(default_fontsize))
default_style = pysubs2.SSAStyle(fontsize=default_fontsize)
subtitle.styles['Default'] = default_style

success, image = vidcap.read()
count = 0
while success:
  fps = vidcap.get(cv2.CAP_PROP_FPS)
  frame_count = int(vidcap.get(cv2.CAP_PROP_FRAME_COUNT))
  duration = count / fps
  seconds = duration % 60
  milliseconds = seconds * 1000
#   print(seconds)
  if milliseconds >= srt_handler.get_start_time_milliseconds():
#   if seconds % 1.0 == 0.0: # every sec
    print("The %dth frame at the %d second will be processed." % (count, seconds))
    print("ANAYD", __file__)
    print("ANAYD2", os.path.abspath(__file__))
    file_dir = os.path.dirname(os.path.abspath(__file__))
    frame_dir = os.path.join(file_dir, "frames", "frame_%d" % count)

    if os.path.isdir(frame_dir):
        shutil.rmtree(frame_dir)
    try:
        os.mkdir(frame_dir)
    except OSError:
        print("Creation of the directory %s failed." % frame_dir)
        raise

    frame_file = os.path.join(frame_dir, "frame_%d.jpg" % count) 
    print("Frame files will be created at: %s." % frame_file)
    cv2.imwrite(frame_file, image)     # save frame as JPEG file     

    x, y = get_coordinates(frame_file, os.path.join(frame_dir, "detection_results"), 'cto', 1000, 130)
    print("The best place has been found at x:%d y:%d position." % (x, y))
    subtitle[srt_handler.get_block_number()].marginl = x
    subtitle[srt_handler.get_block_number()].marginr = width - 1000 - x
    subtitle[srt_handler.get_block_number()].marginv = height - 130 - y
    
    

    if not srt_handler.next():
        break

  success,image = vidcap.read()
#   print('Read a new frame: ', success)
  count += 1

subtitle.save(os.path.join(args['output_ass']))