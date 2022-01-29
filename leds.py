from rpi_ws281x import PixelStrip, Color, WS2811_STRIP_RGB

from skimage.io import imread

width, height = 8, 8
strip = PixelStrip(num=width*height, pin=18, brightness=80, strip_type=WS2811_STRIP_RGB)
strip.begin()

image = imread("./amogus.png")
for x in range(width):
    for y in range(height):
        r, g, b, a = image[x, y]
        a /= 255
        strip.setPixelColor(x*height + y, Color(int(r*a), int(g*a), int(b*a)))

strip.show()
# while True:
#     for i in range(360):
#         r, g, b = colorsys.hsv_to_rgb(i/360, 1, 1)
#         for x in range(strip.numPixels()):
#             strip.setPixelColor(x, Color(int(r*255), int(g*255), int(b*255)))
#         strip.show()
#         time.sleep(0.01)