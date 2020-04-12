import cv2
import os
import subprocess
import shutil
from detector_runner import get_coordinates
from srt_processing import SRTHandler

srt_handler = SRTHandler('test_videos/sky_news_test.srt')
vidcap = cv2.VideoCapture('test_videos/sky_news_test.mp4')
success,image = vidcap.read()
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
    print(seconds)
    file_dir = os.path.dirname(os.path.abspath(__file__))
    frame_dir = os.path.join(file_dir, "frames", "frame_%d" % count)

    if os.path.isdir(frame_dir):
        shutil.rmtree(frame_dir)
    try:
        os.mkdir(frame_dir)
    except OSError:
        print("Creation of the directory %s failed" % frame_dir)
        raise

    frame_file = os.path.join(frame_dir, "frame_%d.jpg" % count) 
    print(frame_file)
    cv2.imwrite(frame_file, image)     # save frame as JPEG file     

    # runner_script = os.path.join(os.path.dirname(file_dir), 'runner', 'runner.py')
    # command = ['python', runner_script,
    #     '--image', frame_file,
    #     '-o', os.path.join(frame_dir, "detection_results"), 
    #     '--detectors', 'ct', '-sh', '130', '-w', '1000']
    # p = subprocess.Popen(" ".join(command), stdout=subprocess.PIPE, shell=True)
    # (output, err) = p.communicate()
    # p_status = p.wait()
    x, y = get_coordinates(frame_file, os.path.join(frame_dir, "detection_results"), 'ct', 1000, 130)
    print("FOUNDED: %d and %d" % (x, y))
    
    if not srt_handler.next():
        break

  success,image = vidcap.read()
#   print('Read a new frame: ', success)
  count += 1