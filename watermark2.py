from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
import matplotlib.pyplot as plt
import numpy as np

# image opening
image = Image.open("images/photos/bec37a7a97774b27a9e8472a4fe4321d.jpeg")
# this open the photo viewer
image.show()  
plt.imshow(image)
 
# text Watermark
watermark_image = image.copy()
 
draw = ImageDraw.Draw(watermark_image)
# ("font type",font size)
w, h = image.size
x, y = int(w / 2), int(h / 2)
if x > y:
  font_size = y
elif y > x:
  font_size = x
else:
  font_size = x
   
font = ImageFont.truetype("/usr/share/fonts/truetype/ubuntu/Ubuntu-R.ttf", int(font_size/6))
 
# add Watermark
# (0,0,0)-black color text
draw.text((x, y), "puppy", fill=(0, 0, 0), font=font, anchor='ms')
plt.subplot(1, 2, 1)
plt.title("black text")
plt.imshow(watermark_image)
 
# add Watermark
# (255,255,255)-White color text
draw.text((x, y), "puppy", fill=(255, 255, 255), font=font, anchor='ms')
plt.subplot(1, 2, 2)
plt.title("white text")
plt.imshow(watermark_image)