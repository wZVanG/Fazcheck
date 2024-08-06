#!/usr/bin/python3

import cairo
import sys
import traceback
import gi
import os

gi.require_version('FPrint', '2.0')
from gi.repository import FPrint, GLib

# Exit with error on any exception, included those happening in async callbacks
sys.excepthook = lambda *args: (traceback.print_exception(*args), sys.exit(1))

def capture_fingerprint(output_path):
    ctx = GLib.main_context_default()
    c = FPrint.Context()
    c.enumerate()
    devices = c.get_devices()

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
            c_buf[y * c_rowstride + x * 4 + 0] = buf[y * width + x]
            c_buf[y * c_rowstride + x * 4 + 1] = buf[y * width + x]
            c_buf[y * c_rowstride + x * 4 + 2] = buf[y * width + x]
            c_buf[y * c_rowstride + x * 4 + 3] = buf[y * width + x]

    c_img.mark_dirty()
    c_img.write_to_png(output_path)

def register_employee():
    document_type = "1"
    document_number = input("Ingrese el DNI del empleado (o '0' para otro tipo de documento): ")

    if document_number == "0":
        print("Seleccione el tipo de documento:")
        print("1: DNI")
        print("2: Pasaporte")
        print("3: Cédula de Identidad")
        print("4: PTP")
        document_type = input("Ingrese el número correspondiente al tipo de documento: ")
        document_number = input("Ingrese el número de documento: ")

    folder_name = f"{document_type}_{document_number}"
    os.makedirs(folder_name, exist_ok=True)

    for i in range(1, 3):
        output_path = os.path.join(folder_name, f'huella_{i}.png')
        print(f"Por favor, coloque su huella {i} vez.")
        capture_fingerprint(output_path)
        print(f"Huellas guardadas en {output_path}")

if __name__ == "__main__":
    for _ in range(1000):
        register_employee()
