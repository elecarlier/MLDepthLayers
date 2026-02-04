import PIL as p
from PIL import Image

img = p.Image.open("./Output/Kim Dungeon 2599-01.jpg")

img = img.convert("L")

img.save("./Output/Kim Dungeon 2599-01_Gray.jpg")

