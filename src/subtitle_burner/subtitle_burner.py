from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw 
import argparse
import os
import textwrap

ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", type=str,
	help="path to input image")
ap.add_argument("-o", "--output", type=str,
	help="path to output image")
ap.add_argument("-x", "--subtitle_x", type=int,
	help="x position of the subtitle")
ap.add_argument("-y", "--subtitle_y", type=int,
	help="y position of the subtitle")
ap.add_argument("-s", "--subtitle_size", type=int,
	help="size of the subtitle", default=24)
ap.add_argument("-sw", "--subtitle_width", type=int,
	help="the width of the subtitle text box")
ap.add_argument("-sh", "--subtitle_height", type=int,
	help="the height of the subtitle text box")
ap.add_argument("-t", "--text", type=str,
	help="the burned text", default=24)



args = vars(ap.parse_args()) 

img = Image.open(args["image"])

draw = ImageDraw.Draw(img)

fonts_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'fonts')
font = ImageFont.truetype(os.path.join(fonts_path, 'Apple Symbols.ttf'), int(args["subtitle_size"]))

text_line_one = textwrap.wrap(str(args["text"]), width=len(str(args["text"]))/2)[0]
text_line_two = textwrap.wrap(str(args["text"]), width=len(str(args["text"]))/2)[1]
line_one_size = font.getsize(text_line_one)
line_two_size = font.getsize(text_line_two)

# Transparenciáról lehet írni a szakdogába
# https://stackoverflow.com/questions/43618910/pil-drawing-a-semi-transparent-square-overlay-on-image#43620169

rectangle_treshold = 5
x = (int(args["subtitle_width"]) - line_one_size[0])/2 + args["subtitle_x"]
y = (int(args["subtitle_height"]/2) - line_one_size[1])/2 + args["subtitle_y"]
draw.rectangle((x-rectangle_treshold,y-rectangle_treshold,x+line_one_size[0]+rectangle_treshold,y+line_one_size[1]+rectangle_treshold), fill=(0,0,0,1))
draw.text((x, y), text_line_one,(255,255,255),font=font)
x = (int(args["subtitle_width"]) - line_two_size[0])/2 + args["subtitle_x"]
y = (int(args["subtitle_height"]) - line_two_size[1]+int(args["subtitle_height"])/2)/2 + args["subtitle_y"]
draw.rectangle((x-rectangle_treshold,y-rectangle_treshold,x+line_two_size[0]+rectangle_treshold,y+line_two_size[1]+rectangle_treshold), fill=(0,0,0,1))
draw.text((x, y), text_line_two,(255,255,255),font=font)

img.save(args["output"] + '/sample-out.png')
