import cv2
import os
import subprocess
import shutil
from detector_runner import get_coordinates
from srt_processing import SRTHandler
import pysubs2
import argparse
import math
from PIL import ImageFont

ap = argparse.ArgumentParser()
ap.add_argument("-is", "--input_srt", type=str,
	help="path to input srt")
ap.add_argument("-iv", "--input_video", type=str,
	help="path to input video (mp4)")
ap.add_argument("-o", "--output_ass", type=str,
	help="path to the output")
args = vars(ap.parse_args()) 

def layout(text, font, max_width):
  width, _ = font.getsize(text)
  devided_texts = []
  space_place = 0
  if width > max_width * 2:
    for char_num in range(int(len(text)/3), int(2 * len(text)/3)):
      if text[char_num] == ' ':
        devided_texts.append(text[:char_num])
        space_place = char_num
        break
    for char_num in range(int(2 * len(text)/3), len(text) - 1):
      if text[char_num] == ' ':
        devided_texts.append(text[space_place+1:char_num])
        space_place = char_num
        break
    devided_texts.append(text[space_place+1:])
  elif width > max_width:
    for char_num in range(int(len(text)/2), len(text)-1):
      if text[char_num] == ' ':
        devided_texts.append(text[:char_num])
        space_place = char_num
        break
    devided_texts.append(text[space_place+1:])
  else:
    devided_texts.append(text)
  return devided_texts


srt_handler = SRTHandler(args['input_srt'])
subtitle = pysubs2.load(args['input_srt'])

vidcap = cv2.VideoCapture(args['input_video'])
frame_width = vidcap.get(cv2.CAP_PROP_FRAME_WIDTH)
height = vidcap.get(cv2.CAP_PROP_FRAME_HEIGHT)
print("The input audio has width:%d and height:%d" % (frame_width, height))

subtitle.info['PlayResX'] = frame_width
subtitle.info['PlayResY'] = height
''' 
Default font size calculated from the (1920x1080) diagonal and 55 fontsize's rate
  sqrt(1920^2 + 1080^2) / 55 = input_diagonal / default_size
'''

fontsize = math.sqrt(frame_width ** 2 + height ** 2) / (math.sqrt(1920 ** 2 + 1080 ** 2) / 55)
print("Default fontsize will be: {}".format(fontsize))

file_dir = os.path.dirname(os.path.abspath(__file__))
font_dir = os.path.join(os.path.dirname(os.path.dirname(file_dir)), 'fonts')
used_font = ImageFont.truetype(os.path.join(font_dir, 'arial.ttf'), int(fontsize))
default_style = pysubs2.SSAStyle(fontsize=fontsize, fontname='Arial')
subtitle.styles['Default'] = default_style

success, image = vidcap.read()
count = 0
while success:
  fps = vidcap.get(cv2.CAP_PROP_FPS)
  frame_count = int(vidcap.get(cv2.CAP_PROP_FRAME_COUNT))
  duration = count / fps
  seconds = duration % 60
  milliseconds = seconds * 1000
  
  if milliseconds >= srt_handler.get_start_time_milliseconds():
#   if seconds % 1.0 == 0.0: # every sec
    print("The %dth frame at the %d second will be processed." % (count, seconds))
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

    text = srt_handler.get_text()
    print("This text will be placed: '{}'".format(text))

    text_lines = layout(text, used_font, int(frame_width / 2))
    print("Text Lines: {}".format(text_lines))
    
    textbox_width, textbox_height = used_font.getsize(max(text_lines, key=len))
    textbox_height = textbox_height * len(text_lines) 
    print("The textbox has {} width and {} height".format(textbox_width, textbox_height))

    x, y = get_coordinates(frame_file, os.path.join(frame_dir, "detection_results"), 'ct', textbox_width, textbox_height)
    print("The best place has been found at x:%d y:%d position.\n" % (x, y))
    subtitle[srt_handler.get_block_number()].marginl = x
    subtitle[srt_handler.get_block_number()].marginr = frame_width - textbox_width - x
    subtitle[srt_handler.get_block_number()].marginv = height - textbox_height - y
    
    

    if not srt_handler.next():
        break

  success,image = vidcap.read()
#   print('Read a new frame: ', success)
  count += 1

subtitle.save(os.path.join(args['output_ass']))