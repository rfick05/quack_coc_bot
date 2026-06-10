import cv2
import pytesseract
import re
import time
from adb_utils import capture_screen


def find_template(device, template_path, threshold=0.85):
    screen = capture_screen(device)
    template = cv2.imread(template_path)

    if screen is None:
        print(f"[{device}] ERROR: screen capture failed")
        return None

    if template is None:
        print(f"ERROR: template not found -> {template_path}")
        return None

    result = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(result)

    if max_val >= threshold:
        h, w = template.shape[:2]
        return (max_loc[0] + w // 2, max_loc[1] + h // 2)

    return None


def wait_for_template(device, template_path, timeout=3, threshold=0.85):
    start = time.time()

    while time.time() - start < timeout:
        coords = find_template(device, template_path, threshold)

        if coords:
            return coords

        time.sleep(0.2)

    return None


def find_all_templates(device, template_path, threshold=0.8, max_results=2):
    """Find up to max_results non-overlapping matches of a template on screen."""
    screen = capture_screen(device)
    template = cv2.imread(template_path)

    if screen is None:
        print(f"[{device}] ERROR: screen capture failed")
        return []

    if template is None:
        print(f"[{device}] WARNING: template not found -> {template_path}")
        return []

    result = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
    h, w = template.shape[:2]
    matches = []

    for _ in range(max_results):
        _, max_val, _, max_loc = cv2.minMaxLoc(result)
        if max_val < threshold:
            break
        cx = max_loc[0] + w // 2
        cy = max_loc[1] + h // 2
        matches.append((cx, cy))
        # Blank out this region so next iteration finds a different match
        x1 = max(0, max_loc[0] - w)
        y1 = max(0, max_loc[1] - h)
        x2 = min(result.shape[1], max_loc[0] + w)
        y2 = min(result.shape[0], max_loc[1] + h)
        result[y1:y2, x1:x2] = 0

    return matches


def read_resources(device):
    """Read gold and elixir values from the scouting screen using OCR.
       Center point is (150, 194), crop ±200 in all directions.
    """
    screen = capture_screen(device)

    if screen is None:
        print(f"[{device}] ERROR: screen capture failed")
        return None, None

    # Gold and elixir are in a tighter top-left crop for resource checking
    x1, y1, x2, y2 = 90, 150, 250, 250
    crop = screen[y1:y2, x1:x2]

    # Scale up 2x for better OCR accuracy
    scale = 2
    h, w = crop.shape[:2]
    crop = cv2.resize(crop, (w * scale, h * scale), interpolation=cv2.INTER_CUBIC)

    gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    text = pytesseract.image_to_string(
        thresh,
        config="--psm 6 -c tessedit_char_whitelist=0123456789,"
    )

    # Strip commas/dots before parsing
    text_clean = text.replace(",", "").replace(".", "")
    print(f"[{device}] OCR raw text: '{text.strip()}'")
    numbers = [int(n) for n in re.findall(r"\d{4,8}", text_clean) if int(n) <= 10_000_000]
    print(f"[{device}] OCR numbers found: {numbers}")

    if len(numbers) >= 2:
        return numbers[0], numbers[1]
    elif len(numbers) == 1:
        return numbers[0], None
    return None, None


def read_trophies(device):
    screen = capture_screen(device)

    if screen is None:
        print(f"[{device}] ERROR: screen capture failed")
        return None

    import json, os
    CONFIG_PATH = os.path.join(os.path.dirname(__file__), "../config.json")

    with open(CONFIG_PATH, "r") as f:
        config = json.load(f)

    roi = config["trophy_roi"]
    x1, y1, x2, y2 = roi["x1"], roi["y1"], roi["x2"], roi["y2"]

    crop = screen[y1:y2, x1:x2]
    gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 100, 255, cv2.THRESH_BINARY)

    text = pytesseract.image_to_string(
        thresh,
        config="--psm 7 -c tessedit_char_whitelist=0123456789"
    )

    match = re.findall(r"\d+", text)
    return int(match[0]) if match else None
