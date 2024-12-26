from PIL import Image
import matplotlib.pyplot as plt
import numpy as np
# text Watermark
from PIL import ImageFont
from PIL import ImageDraw


name = "images/photos/bec37a7a97774b27a9e8472a4fe4321d.jpeg"
image = Image.open(name)
 
# this open the photo viewer
image.show() 
plt.imshow(image)

watermark_image = image.copy()
 
draw = ImageDraw.Draw(watermark_image)
 
w, h = image.size
x, y = int(w / 2), int(h / 2)
if x > y:
  font_size = y
elif y > x:
  font_size = x
else:
  font_size = x

  ImageFont.truetype
   
font = ImageFont.truetype("/usr/share/fonts/truetype/ubuntu/Ubuntu-R.ttf", int(font_size/6))
 
# add watermark
draw.text((x, y), "puppy", fill=(0, 0, 0), font=font, anchor='ms')
plt.subplot(1, 2, 1)
plt.title("black text")
plt.imshow(watermark_image)
 
# add watermark
draw.text((x, y), "puppy", fill=(255, 255, 255), font=font, anchor='ms')
plt.subplot(1, 2, 2)
plt.title("white text")
plt.imshow(watermark_image)
