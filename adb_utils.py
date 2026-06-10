import subprocess
import random
import numpy as np
import cv2


def get_devices():
    result = subprocess.check_output("adb devices", shell=True).decode()
    lines = result.strip().split("\n")[1:]

    devices = []

    for line in lines:
        if "\tdevice" in line:
            devices.append(line.split()[0])

    return devices


def adb_tap(device, x, y):
    subprocess.run([
        "adb", "-s", device,
        "shell", "input", "tap",
        str(x), str(y)
    ])


def adb_swipe(device, x1, y1, x2, y2, duration=200):
    subprocess.run([
        "adb", "-s", device,
        "shell", "input", "swipe",
        str(x1), str(y1),
        str(x2), str(y2),
        str(duration)
    ])


def capture_screen(device):
    raw = subprocess.check_output(
        f"adb -s {device} exec-out screencap -p",
        shell=True
    )

    img_array = np.frombuffer(raw, dtype=np.uint8)
    img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

    return img