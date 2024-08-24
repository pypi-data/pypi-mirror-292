
# -------------------------------------------------------------
# This is not production code but I am losing the will to live
# Provide the path to the module so that the tests can run
import os
import sys
import piexif
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
# --------------------------------------------------------------

from picamzero import Camera
from time import sleep

cam = Camera()
cam.brightness = 0.7
cam.take_photo("eetgetere")
print(cam.brightness)
