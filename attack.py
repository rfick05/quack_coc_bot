import time
import random
from adb_utils import adb_tap, adb_swipe
from image_utils import wait_for_template
from coordinates import COORDS


def jitter_coord(x, y, jitter_range=10):
    return x + random.randint(-jitter_range, jitter_range), y + random.randint(-jitter_range, jitter_range)


def get_drop_coords(number=1):
    rage_mid = (1202, 104)
    rage_top = (1197, 238)
    rage_bot = (1190, 725)
    rage2_right_up = (935, 345)
    rage2_right_down = (935, 570)
    rage2_left_up = (1400, 345)
    rage2_left_down = (1400, 570)

    if number == 1:
        left_x = random.randint(78, 110)
        right_x = random.randint(480, 514)
        mid_x = random.randint(269, 310)
        left_y = round(-0.8165 * left_x + 542.68)
        right_y = round(-0.8165 * right_x + 542.68)
        mid_y = round(-0.8165 * mid_x + 542.68)
        return left_x, left_y, right_x, right_y, mid_x, mid_y, rage_mid, rage_top, rage_bot, rage2_right_up, rage2_right_down

    elif number == 2:
        left_x = random.randint(120, 150)
        right_x = random.randint(350, 400)
        mid_x = random.randint(220, 280)
        left_y = round(0.865 * left_x + 376.2)
        right_y = round(0.865 * right_x + 376.2)
        mid_y = round(0.865 * mid_x + 376.2)
        return left_x, left_y, right_x, right_y, mid_x, mid_y, rage_mid, rage_top, rage_bot, rage2_right_up, rage2_right_down

    elif number == 3:
        left_x = random.randint(1755, 1795)
        right_x = random.randint(2270, 2318)
        mid_x = random.randint(1990, 2060)
        left_y = round(0.74 * left_x - 1120)
        right_y = round(0.74 * right_x - 1120)
        mid_y = round(0.74 * mid_x - 1120)
        return left_x, left_y, right_x, right_y, mid_x + 5, mid_y, rage_mid, rage_top, rage_bot, rage2_left_up, rage2_left_down


def find_attack(device, drop=True):
    adb_tap(device, 158 + random.randint(-5, 5), 951 + random.randint(-5, 5))
    time.sleep(random.uniform(0.5, 1))
    adb_tap(device, 158 + random.randint(-5, 5), 951 + random.randint(-5, 5))
    time.sleep(0.3)

    adb_tap(device, COORDS["backup_attack"][0], COORDS["backup_attack"][1])
    time.sleep(random.uniform(0.5, 1))

    match_btn = wait_for_template(device, "templates/find_match.png", timeout=5)
    if match_btn:
        adb_tap(device, match_btn[0], match_btn[1])
    else:
        adb_tap(device, 386, 786)

    time.sleep(random.uniform(0.5, 1))

    adb_tap(device, 1900 + random.randint(-5, 5), 990 + random.randint(-5, 5))
    time.sleep(random.uniform(1, 2))

    drop_attack(device)

    print(f"[{device}] Waiting for battle to end...")
    timeout = 200
    start_time = time.time()

    while time.time() - start_time < timeout:
        ret_home = wait_for_template(device, "templates/return_home.png", timeout=3)
        if ret_home:
            print(f"[{device}] Battle ended")
            for _ in range(2):
                adb_tap(device,
                        ret_home[0] + random.randint(-40, 40),
                        ret_home[1] + random.randint(-40, 40))
                time.sleep(random.uniform(0.2, 0.3))
            break
        time.sleep(1)


def drop_attack(device):
    attack_strat = random.randint(1, 3)
    left_x, left_y, right_x, right_y, mid_x, mid_y, rage_mid, rage_top, rage_bot, rage2_right_up, rage2_right_down = get_drop_coords(attack_strat)

    wait_for_template(device, "templates/next_button.png", timeout=15)

    attack(device, attack_strat, mid_x, mid_y)


def attack(device, attack_strat, mid_x, mid_y):
    print(f"[{device}] Centering view...")
    adb_tap(device, 960, 540)
    time.sleep(0.5)
    adb_tap(device, 960, 540)
    time.sleep(0.5)
    print(f"[{device}] Starting attack sequence...")

    next_btn = wait_for_template(device, "templates/next_button.png", timeout=15)

    jitter_x = random.randint(-40, 40)
    jitter_y = random.randint(-40, 40)

    # === Siege ===
    adb_tap(device, *jitter_coord(786, 992))
    time.sleep(random.uniform(0.1, 0.3))
    adb_tap(device, mid_x, mid_y)

    # === Electro Titans ===
    adb_tap(device, *jitter_coord(592, 975))
    time.sleep(random.uniform(0.1, 0.3))
    for _ in range(4):
        adb_tap(device, mid_x, mid_y)
        time.sleep(random.uniform(0.1, 0.2))
    time.sleep(random.uniform(0.1, 0.3))

    # === Yeti ===
    adb_tap(device, *jitter_coord(457, 977))
    time.sleep(random.uniform(0.2, 0.3))
    for _ in range(10):
        adb_tap(device, mid_x, mid_y)
        time.sleep(random.uniform(0.1, 0.2))

    # === King ===
    adb_tap(device, *jitter_coord(941, 946))
    time.sleep(random.uniform(0.15, 0.4))
    adb_tap(device, mid_x, mid_y)
    time.sleep(random.uniform(0.15, 0.25))
    adb_tap(device, mid_x, mid_y)
    time.sleep(random.uniform(0.15, 0.25))

    # === Queen ===
    adb_tap(device, *jitter_coord(1084, 951))
    time.sleep(random.uniform(0.15, 0.3))
    adb_tap(device, mid_x, mid_y)
    time.sleep(random.uniform(0.15, 0.3))
    adb_tap(device, mid_x, mid_y)
    time.sleep(random.uniform(0.15, 0.3))

    # === Warden ===
    adb_tap(device, *jitter_coord(1230, 942))
    time.sleep(random.uniform(0.15, 0.3))
    adb_tap(device, mid_x, mid_y)
    time.sleep(random.uniform(0.15, 0.3))
    adb_tap(device, mid_x, mid_y)
    time.sleep(random.uniform(0.15, 0.3))

    # === Royal Champion ===
    adb_tap(device, *jitter_coord(1376, 949))
    time.sleep(random.uniform(0.1, 0.3))
    adb_tap(device, mid_x, mid_y)
    time.sleep(random.uniform(0.15, 0.25))
    adb_tap(device, mid_x, mid_y)
    time.sleep(random.uniform(0.15, 0.25))

    # === Warden Again ===
    time.sleep(random.uniform(0.5, 0.8))
    adb_tap(device, *jitter_coord(1230, 942))
    time.sleep(random.uniform(0.2, 0.4))

    # === King Again ===
    adb_tap(device, *jitter_coord(941, 946))
    time.sleep(random.uniform(0.2, 0.4))

    if attack_strat == 2:
        adb_tap(device, 1654 + random.randint(-7, 7), 965 + random.randint(-7, 7))
        for x, y in [(988, 704), (791, 448), (1122, 535), (1026, 608), (1036, 360), (1351, 686)]:
            time.sleep(random.uniform(0.2, 0.4))
            adb_tap(device, x + random.randint(-7, 7), y + random.randint(-7, 7))

    elif attack_strat == 3:
        adb_tap(device, 1654 + random.randint(-7, 7), 965 + random.randint(-7, 7))
        for x, y in [(1258, 270), (1380, 483), (1408, 685), (1300, 522), (1285, 644)]:
            time.sleep(random.uniform(0.2, 0.4))
            adb_tap(device, x + random.randint(-7, 7), y + random.randint(-7, 7))

    # === Rage Sequence ===
    if attack_strat == 1:
        time.sleep(random.uniform(9, 11))
        jitter_x = random.randint(-10, 10)
        jitter_y = random.randint(-10, 10)
        adb_tap(device, *jitter_coord(1513, 970))
        time.sleep(random.uniform(0.3, 0.6))
        adb_tap(device, COORDS["rage_fallback1"][0] + jitter_x, COORDS["rage_fallback1"][1] + jitter_y)
        time.sleep(random.uniform(0.5, 0.8))
        adb_tap(device, COORDS["rage_fallback2"][0] + jitter_x, COORDS["rage_fallback2"][1] + jitter_y)
        time.sleep(random.uniform(0.3, 0.6))
        adb_tap(device, COORDS["rage_fallback3"][0] + jitter_x, COORDS["rage_fallback3"][1] + jitter_y)
        time.sleep(random.uniform(5, 8))
        adb_tap(device, *jitter_coord(1513, 970))
        adb_tap(device, COORDS["rage_fallback4"][0] + jitter_x, COORDS["rage_fallback4"][1] + jitter_y)
        time.sleep(random.uniform(0.5, 1))
        adb_tap(device, COORDS["rage_fallback5"][0] + jitter_x, COORDS["rage_fallback5"][1] + jitter_y)

    elif attack_strat == 2:
        time.sleep(random.uniform(15, 25))
        adb_tap(device, *jitter_coord(1513, 970))
        for x, y in [(1013, 307), (1035, 513), (1055, 689), (1409, 477), (1421, 679)]:
            adb_tap(device, x + random.randint(-7, 7) + 15, y + random.randint(-7, 7))
            time.sleep(random.uniform(0.3, 0.6))

    elif attack_strat == 3:
        time.sleep(random.uniform(15, 25))
        adb_tap(device, *jitter_coord(1513, 970))
        for x, y in [(1258, 270), (1380, 483), (1408, 685), (900, 400), (980, 600)]:
            adb_tap(device, x + random.randint(-7, 7) - 40, y + random.randint(-7, 7))
            time.sleep(random.uniform(0.3, 0.6))