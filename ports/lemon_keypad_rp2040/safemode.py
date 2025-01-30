import board
import neopixel
import storage
import os

pixel_pin = board.GP7
num_pixels = 6


# load neopixel and set all led to green to indicate that it's safe mode.
color = (0, 0x20, 0)
pixels = neopixel.NeoPixel(pixel_pin, num_pixels)
pixels.fill(color)
