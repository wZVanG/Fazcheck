#!/usr/bin/python3

import cairo
import sys
import traceback
import gi

gi.require_version('FPrint', '2.0')
from gi.repository import FPrint, GLib

# Exit with error on any exception, included those happening in async callbacks
sys.excepthook = lambda *args: (traceback.print_exception(*args), sys.exit(1))

if len(sys.argv) != 2:
    print("Please specify exactly one argument, the output location for the capture image")
    sys.exit(1)

ctx = GLib.main_context_default()

c = FPrint.Context()
c.enumerate()
devices = c.get_devices()

# Imprimir los dispositivos disponibles
for i, d in enumerate(devices):
    print(f"Device {i}: {d.get_name()}")

d = devices[0]
assert d.has_feature(FPrint.DeviceFeature.CAPTURE)
assert d.has_feature(FPrint.DeviceFeature.IDENTIFY)
assert d.has_feature(FPrint.DeviceFeature.VERIFY)
assert not d.has_feature(FPrint.DeviceFeature.DUPLICATES_CHECK)
assert not d.has_feature(FPrint.DeviceFeature.STORAGE)
assert not d.has_feature(FPrint.DeviceFeature.STORAGE_LIST)
assert not d.has_feature(FPrint.DeviceFeature.STORAGE_DELETE)
assert not d.has_feature(FPrint.DeviceFeature.STORAGE_CLEAR)
del devices

d.open_sync()

img = d.capture_sync(True)

d.close_sync()

del d
del c

width = img.get_width()
height = img.get_height()

c_img = cairo.ImageSurface(cairo.FORMAT_RGB24, width, height)

c_rowstride = c_img.get_stride()

buf = img.get_data()
c_buf = c_img.get_data()

for x in range(width):
    for y in range(height):
        # The upper byte is don't care, but the location depends on endianness,
        # so just set all of them.
        c_buf[y * c_rowstride + x * 4 + 0] = buf[y * width + x]
        c_buf[y * c_rowstride + x * 4 + 1] = buf[y * width + x]
        c_buf[y * c_rowstride + x * 4 + 2] = buf[y * width + x]
        c_buf[y * c_rowstride + x * 4 + 3] = buf[y * width + x]

c_img.mark_dirty()
c_img.write_to_png(sys.argv[1])
