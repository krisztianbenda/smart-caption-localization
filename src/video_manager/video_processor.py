import cv2
import os
import subprocess
import shutil
from detector_runner import get_coordinates, ImageHandler
from srt_processing import SRTHandler
import pysubs2
from pysubs2 import SSAEvent, SSAFile
import argparse
import math
from PIL import ImageFont
from position_collector import PositionCollector

ap = argparse.ArgumentParser()
ap.add_argument("-is", "--input_srt", type=str,
	help="path to input srt")
ap.add_argument("-iv", "--input_video", type=str,
	help="path to input video (mp4)")
ap.add_argument("-o", "--output_ass", type=str,
	help="path to the output")
ap.add_argument("-d", "--detectors", type=str,
	help="used detectors. c: canny edge, t:text, l:logo, o:object")
ap.add_argument("-a", "--algorithm", type=str, default="fix",
  help="the used algorithms. Options are fix, dynamic and stable")
ap.add_argument("-r", "--resolution", type=float, default="3",
  help="the used resolution for the algorithm in seconds")
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

def create_dir(frame_dir):
  if os.path.isdir(frame_dir):
    shutil.rmtree(frame_dir)
  try:
    os.mkdir(frame_dir)
  except OSError:
    print("Creation of the directory %s failed." % frame_dir)
    raise

def get_frame_number(from_millisecond, fps) -> int:
  fpms = fps/1000 # frame per millisecond
  return int(from_millisecond * fpms) + 1 # round up

def get_textbox_size(text, used_font, frame_width) -> (float, float):
  print("This text will be placed: '{}'".format(text))
  text_lines = layout(text, used_font, int(frame_width / 2))
  print("Text Lines: {}".format(text_lines))
  textbox_width, textbox_height = used_font.getsize(max(text_lines, key=len))
  textbox_height = textbox_height * len(text_lines)
  print("The textbox has {} width and {} height".format(textbox_width, textbox_height))
  return (textbox_width, textbox_height)

def get_block_number(subtitle: SSAFile, second):
  for i in range(0, len(subtitle.events)):
    if subtitle.events[i].start <= second * 1000 and second * 1000 < subtitle.events[i].end:
      return i
  return None

def new_block_start(subtitle, video_duration, previous_text):
  return (get_block_number(subtitle, video_duration) != None 
    and previous_text != subtitle[get_block_number(subtitle, video_duration)].text)

def persistent_frame(frame_dir, frame_num):
  frame_name = "frame_%d" % frame_num
  frame_dir_name = os.path.join(frame_dir, frame_name)
  create_dir(frame_dir_name)
  frame_file = os.path.join(frame_dir_name, frame_name + '.jpg')
  cv2.imwrite(frame_file, image)
  return frame_dir_name, frame_file
  

srt_handler = SRTHandler(args['input_srt'])
subtitle = pysubs2.load(args['input_srt'])
vidcap = cv2.VideoCapture(args['input_video'])

frame_width = vidcap.get(cv2.CAP_PROP_FRAME_WIDTH)
frame_height = vidcap.get(cv2.CAP_PROP_FRAME_HEIGHT)
print("The input audio has width:%d and height:%d" % (frame_width, frame_height))

subtitle.info['PlayResX'] = frame_width
subtitle.info['PlayResY'] = frame_height
''' 
Default font size calculated from the (1920x1080) diagonal and 54 fontsize's rate
  sqrt(1920^2 + 1080^2) / 54 = input_diagonal / default_size
'''

fontsize = int(math.sqrt(frame_width ** 2 + frame_height ** 2) / (math.sqrt(1920 ** 2 + 1080 ** 2) / 54))
print("Default fontsize will be: {}".format(fontsize))

file_dir = os.path.dirname(os.path.abspath(__file__))
font_dir = os.path.join(os.path.dirname(os.path.dirname(file_dir)), 'fonts')
used_font = ImageFont.truetype(os.path.join(font_dir, 'arial.ttf'), int(fontsize))
default_style = pysubs2.SSAStyle(fontsize=fontsize, fontname='Arial')
subtitle.styles['Default'] = default_style

success, image = vidcap.read()
count = 0

algorithm = str(args['algorithm'])
position_collector = PositionCollector(max_distance=8)
print("-------ALGORITHM: {}-------".format(algorithm.upper()))
if algorithm == 'dynamic':
  time_resolution = float(args['resolution'])
  time = 0
  frame_dir = os.path.join(file_dir, "frames_dynamic")
  create_dir(frame_dir)
  transcript_block_image_handler = ImageHandler()
  # set default place
  x = int(frame_width/3)
  y = int(8*frame_height/10)
  textbox_width = int(frame_width/3)
  textbox_height = int(frame_height/10)

  previous_text = ""
  while success:
    fps = vidcap.get(cv2.CAP_PROP_FPS)
    frame_count = int(vidcap.get(cv2.CAP_PROP_FRAME_COUNT))
    video_duration = count / fps
    
    if srt_handler.get_by_second(time) is '':
      # print("Subtitle does not found at {} time".format(time))
      time = time + time_resolution
    elif video_duration >= time:

      print("\nProcessing start at %dth frame, video frame duration is: %f the time is: %f" % (count, video_duration, time))
      print("fps: %d" % fps)
      frame_name = "frame_%d" % count
      print(frame_name + " will be processed.")
      frame_dir_name, frame_file = persistent_frame(frame_dir, count)

      text = srt_handler.get_by_second(time)
      if text != previous_text:
        print("The previous text was: %s" % previous_text)
        position_collector.new_block()
        previous_text = text

      textbox_width, textbox_height = get_textbox_size(text, used_font, frame_width)
      x, y = get_coordinates(ImageHandler().add_image(frame_file), 
        os.path.join(frame_dir_name, "detection_results"), 
        args['detectors'], textbox_width, textbox_height)
      print("The best place has been found at x:%d y:%d position." % (x, y))
      print("The previous place was x:%d y:%d" % position_collector.get_current())
      position_collector.add((x,y))
      corrected_x, corrected_y = position_collector.correct_position()
      print("The positions were corrected to x:%d -> %d y:%d -> %d position." % (x, corrected_x, y, corrected_y))

      original_block_number = get_block_number(subtitle, time)
      event = SSAEvent(start=int(time * 1000), #start is in millisecond 
        end=subtitle[original_block_number].end, 
        text=subtitle[original_block_number].text,
        marginl= corrected_x,
        marginr= frame_width - textbox_width - corrected_x,
        marginv= frame_height - textbox_height - corrected_y
        )
      print("This event will be placed: {}".format(event.__dict__))
      subtitle.insert(original_block_number+1, event)
      # subtitle[original_block_number].end = int(time * 1000) # end is in millisecond
      subtitle[original_block_number].end = event.start
      print("The previous was modified to: {}".format(subtitle[original_block_number].__dict__))
      time = time + time_resolution
    elif new_block_start(subtitle, video_duration, previous_text):
      print("\nNew Transcript block start without time trigger")
      print("Processing start at %dth frame, video frame duration is: %f the time is: %f" % (count, video_duration, time))
      frame_dir_name, frame_file = persistent_frame(frame_dir, count)
      text = srt_handler.get_by_second(video_duration)
      print("The previous text was: %s" % previous_text)
      position_collector.new_block()
      previous_text = text
      
      textbox_width, textbox_height = get_textbox_size(text, used_font, frame_width)
      x, y = get_coordinates(ImageHandler().add_image(frame_file), 
        os.path.join(frame_dir_name, "detection_results"), 
        args['detectors'], textbox_width, textbox_height)
      print("The best place has been found at x:%d y:%d position." % (x, y))
      print("The previous place was x:%d y:%d" % position_collector.get_current())
      position_collector.add((x,y))

      original_block_number = get_block_number(subtitle, video_duration)
      event = SSAEvent(start=int(video_duration * 1000), #start is in millisecond 
        end=subtitle[original_block_number].end, 
        text=subtitle[original_block_number].text,
        marginl= x,
        marginr= frame_width - textbox_width - x,
        marginv= frame_height - textbox_height - y
        )
      print("The event will be modified to this: {}".format(event.__dict__))
      subtitle[original_block_number] = event

    success,image = vidcap.read()
    count += 1

elif algorithm == "fix":
  time_resolution = float(args['resolution'])
  time = 0
  frame_dir = os.path.join(file_dir, "frames_{}".format(algorithm))
  create_dir(frame_dir)
  transcript_block_image_handler = ImageHandler()
  fps = vidcap.get(cv2.CAP_PROP_FPS)
  max_textbox_width = 0
  max_textbox_height = 0
  previous_text = ''
  while success:
    frame_count = int(vidcap.get(cv2.CAP_PROP_FRAME_COUNT))
    video_duration = count / fps

    if srt_handler.get_by_second(time) is '':
      time = time + time_resolution
    elif video_duration >= time:
      print('\n====== Detecting the %d frame at %f second in the video ======' % (count, video_duration))
      frame_file = os.path.join(frame_dir, "frame_%d.jpg" % count) 
      print("Frame file will be created at: %s." % frame_file)
      cv2.imwrite(frame_file, image)     # save frame as JPEG file     
      transcript_block_image_handler.add_image(frame_file)

      text = srt_handler.get_by_second(video_duration)
      if text != previous_text:
        print("The previous text was: %s" % previous_text)
        previous_text = text
        textbox_width, textbox_height = get_textbox_size(text, used_font, frame_width)
        if textbox_width > max_textbox_width:
          max_textbox_width = textbox_width
        if textbox_height > max_textbox_height:
          max_textbox_height = textbox_height

      time = time + time_resolution

    success,image = vidcap.read()
    count += 1
  
  # default place
  x = int(frame_width/3)
  y = int(8*frame_height/10)
  x, y = get_coordinates(transcript_block_image_handler, os.path.join(frame_dir, "detection_results"), args['detectors'], textbox_width, textbox_height)
  print("The best place has been found at x:%d y:%d position.\n" % (x, y))
  for block in subtitle:
    block.marginl = x
    block.marginr = frame_width - max_textbox_width - x
    block.marginv = frame_height - max_textbox_height - y

elif algorithm == "stable":
  transcript_block_start = 0
  transcript_block_image_handler = ImageHandler()
  is_transcript_block_start_processed = False
  is_transcript_block_middle_processed = False
  text, text_lines, textbox_width, textbox_height = "", [""], 0,0
  frame_dir = ""
  while success:
    fps = vidcap.get(cv2.CAP_PROP_FPS)
    frame_count = int(vidcap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = count / fps
    # seconds = duration % 60
    seconds = duration
    milliseconds = seconds * 1000
    
    if milliseconds >= srt_handler.get_end_time_ms():
      print("======= Detecting END of transcript block =======")
      print("Transcript block ENDs at %d millisecond" % milliseconds)
      print("The %dth frame at the %d second will be processed." % (count, seconds))
      print("The following directory will be used for frames: \n{}".format(frame_dir))
      
      frame_file = os.path.join(frame_dir, "frame_%d.jpg" % count) 
      print("Frame file will be created at: %s." % frame_file)
      cv2.imwrite(frame_file, image)     # save frame as JPEG file     

      transcript_block_image_handler.add_image(frame_file)
      x, y = get_coordinates(transcript_block_image_handler, os.path.join(frame_dir, "detection_results"), args['detectors'], textbox_width, textbox_height)
      print("The best place has been found at x:%d y:%d position.\n" % (x, y))
      subtitle[srt_handler.get_block_number()].marginl = x
      subtitle[srt_handler.get_block_number()].marginr = frame_width - textbox_width - x
      subtitle[srt_handler.get_block_number()].marginv = frame_height - textbox_height - y
      
      transcript_block_image_handler = ImageHandler()
      is_transcript_block_start_processed = False
      is_transcript_block_middle_processed = False
      if not srt_handler.next():
          break
    
    elif milliseconds >= srt_handler.get_middle_time_ms() and not is_transcript_block_middle_processed:
      print("======= Detecting MIDDLE of transcript block =======")
      print("Transcript block MID is at %d milliseconds" % milliseconds)
      print("The %dth frame at the %d second will be processed." % (count, seconds))
      print("The following directory will be used for frames: \n{}".format(frame_dir))
      
      frame_file = os.path.join(frame_dir, "frame_%d.jpg" % count) 
      print("Frame file will be created at: %s." % frame_file)
      cv2.imwrite(frame_file, image)     # save frame as JPEG file     
      transcript_block_image_handler.add_image(frame_file)
      x, y = get_coordinates(transcript_block_image_handler, 
        os.path.join(frame_dir, "detection_results"), args['detectors'], textbox_width, textbox_height)
      print("The best place has been found at x:%d y:%d position.\n" % (x, y))

      is_transcript_block_middle_processed = True

    elif milliseconds >= srt_handler.get_start_time_milliseconds() and not is_transcript_block_start_processed:
      print("\n\n======= Detecting START of transcript block =======")
      print("Transcript block STARTs at %d milliseconds" % milliseconds)
      print("The %dth frame at the %d second will be processed." % (count, seconds))
      frame_dir = os.path.join(file_dir, "frames_stable", "frame_%d-%d-%d" % 
        (count, get_frame_number(srt_handler.get_middle_time_ms(), fps), get_frame_number(srt_handler.get_end_time_ms(), fps)))
      create_dir(frame_dir=frame_dir)

      frame_file = os.path.join(frame_dir, "frame_%d.jpg" % count) 
      print("Frame file will be created at: %s." % frame_file)
      cv2.imwrite(frame_file, image)     # save frame as JPEG file   

      text = srt_handler.get_text()
      textbox_width, textbox_height = get_textbox_size(text, used_font, frame_width)
      transcript_block_image_handler.add_image(frame_file)
      x, y = get_coordinates(transcript_block_image_handler, 
        os.path.join(frame_dir, "detection_results"), args['detectors'], textbox_width, textbox_height)
      print("The best place has been found at x:%d y:%d position.\n" % (x, y))

      transcript_block_start = count
      is_transcript_block_start_processed = True


    success,image = vidcap.read()
    count += 1

subtitle.save("%s_%s_%s_%f.ass" % (os.path.join(args['output_ass'])[:-4], algorithm, args['detectors'], float(args['resolution'])))
if algorithm == "dynamic":
  print('Collected positions are: ')
  position_collector.print()