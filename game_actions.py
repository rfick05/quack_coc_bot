import time
import random
from adb_utils import adb_tap, adb_swipe
from image_utils import wait_for_template, read_resources
from coordinates import COORDS

TROOP_Y = 970
RAGE_X = 1400
OVERGROWTH_X = 1600  # rage + 200


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
        print("Using attack strategy 1.")
        left_x = random.randint(78, 110)
        right_x = random.randint(480, 514)
        mid_x = random.randint(269, 310)
        left_y = round(-0.8165 * left_x + 542.68)
        right_y = round(-0.8165 * right_x + 542.68)
        mid_y = round(-0.8165 * mid_x + 542.68)
        return left_x, left_y, right_x, right_y, mid_x, mid_y, rage_mid, rage_top, rage_bot, rage2_right_up, rage2_right_down
    elif number == 2:
        print("Using attack strategy 2.")
        left_x = random.randint(120, 150)
        right_x = random.randint(350, 400)
        mid_x = random.randint(220, 280)
        left_y = round(0.865 * left_x + 376.2)
        right_y = round(0.865 * right_x + 376.2)
        mid_y = round(0.865 * mid_x + 376.2)
        return left_x, left_y, right_x, right_y, mid_x, mid_y, rage_mid, rage_top, rage_bot, rage2_right_up, rage2_right_down
    elif number == 3:
        print("Using attack strategy 3.")
        left_x = random.randint(1755, 1795)
        right_x = random.randint(2270, 2318)
        mid_x = random.randint(1990, 2060)
        left_y = round(0.74 * left_x - 1120)
        right_y = round(0.74 * right_x - 1120)
        mid_y = round(0.74 * mid_x - 1120)
        return left_x, left_y, right_x, right_y, mid_x + 5, mid_y, rage_mid, rage_top, rage_bot, rage2_left_up, rage2_left_down


def check_resources(device):
    gold, elixir = read_resources(device)
    print(f"[{device}] Resources — Gold: {gold}, Elixir: {elixir}")

    if gold is None and elixir is None:
        print(f"[{device}] Could not read resources, skipping base.")
        return False

    # Use whichever values we have
    g = gold or 0
    e = elixir or 0

    if g >= 1_000_000 or e >= 1_000_000:
        print(f"[{device}] One resource over 1M, attacking!")
        return True

    if g >= 700_000 and e >= 700_000:
        print(f"[{device}] Both resources over 700k, attacking!")
        return True

    print(f"[{device}] Resources too low, skipping base.")
    return False


def find_attack(device):
    # Start matchmaking
    time.sleep(random.uniform(0, 1))

    print(f"[{device}] Clicking primary attack button...")
    adb_tap(device, 158 + random.randint(-5, 5), 951 + random.randint(-5, 5))
    time.sleep(random.uniform(0.5, 1))

    print(f"[{device}] Using backup attack button...")
    adb_tap(device, COORDS["backup_attack"][0], COORDS["backup_attack"][1])
    time.sleep(random.uniform(0, 1))

    print(f"[{device}] Searching for 'find match' button...")
    match_btn = wait_for_template(device, "templates/find_match.png", timeout=3)
    if match_btn:
        print(f"[{device}] Found 'find match' button at:", match_btn)
        adb_tap(device, match_btn[0], match_btn[1])
    else:
        print(f"[{device}] Find match button not found, using fallback.")
        adb_tap(device, 386, 786)

    time.sleep(random.uniform(0.5, 1))

    print(f"[{device}] Pressing confirm attack button...")
    adb_tap(device, 1900 + random.randint(-5, 5), 990 + random.randint(-5, 5))
    time.sleep(random.uniform(1, 2))

    # Keep hitting next until we find a base worth attacking
    while True:
        next_btn = wait_for_template(device, "templates/next_button.png", timeout=30)
        if not next_btn:
            print(f"[{device}] Next button not found, retrying...")
            time.sleep(5)
            continue

        print(f"[{device}] Checking resources...")
        time.sleep(random.uniform(0.3, 0.6))

        if not check_resources(device):
            # Tap next to get a new base
            adb_tap(device, next_btn[0] + random.randint(-20, 20), next_btn[1] + random.randint(-10, 10))
            time.sleep(random.uniform(0.5, 0.8))
            continue

        # Good base — do NOT tap next, just go straight into attack
        print(f"[{device}] Good base found, attacking!")
        time.sleep(random.uniform(0.3, 0.6))
        attack(device)
        return



def attack(device):
    print(f"[{device}] Centering view...")
    adb_tap(device, 960, 540)
    time.sleep(0.5)
    adb_tap(device, 960, 540)
    time.sleep(0.5)
    print(f"[{device}] Starting attack sequence...")

    attack_strat = random.randint(2, 3)
    left_x, left_y, right_x, right_y, mid_x, mid_y, rage_mid, rage_top, rage_bot, rage2_right_up, rage2_right_down = get_drop_coords(attack_strat)

    wait_for_template(device, "templates/next_button.png", timeout=15)

    # === Rage spell (x=1400) — drop in middle ===
    print(f"[{device}] Casting rage spell...")
    adb_tap(device, RAGE_X + random.randint(-7, 7), TROOP_Y + random.randint(-7, 7))
    time.sleep(random.uniform(0.2, 0.4))
    adb_tap(device, mid_x + random.randint(-30, 30), mid_y + random.randint(-30, 30))
    time.sleep(random.uniform(0.3, 0.5))

    # === Overgrowth spell (x=1600) — drop in middle ===
    print(f"[{device}] Casting overgrowth spell...")
    adb_tap(device, OVERGROWTH_X + random.randint(-7, 7), TROOP_Y + random.randint(-7, 7))
    time.sleep(random.uniform(0.2, 0.4))
    adb_tap(device, mid_x + random.randint(-30, 30), mid_y + random.randint(-30, 30))
    time.sleep(random.uniform(0.3, 0.5))

    # === Edrags x11 — spread across a line centered on mid for human-like placement ===
    print(f"[{device}] Deploying edrags...")
    adb_tap(device, 432 + random.randint(-7, 7), TROOP_Y + random.randint(-7, 7))
    time.sleep(random.uniform(0.2, 0.4))
    for i in range(11):
        # Spread across ~120px wide zone, slight y variance
        offset_x = int((i - 5) * 12) + random.randint(-8, 8)
        offset_y = random.randint(-12, 12)
        adb_tap(device, mid_x + offset_x, mid_y + offset_y)
        time.sleep(random.uniform(0.15, 0.28))

    print(f"[{device}] Deploying siege and heroes...")
    # === Siege ===
    adb_tap(device, 590 + random.randint(-7, 7), TROOP_Y + random.randint(-7, 7))
    time.sleep(random.uniform(0.1, 0.3))
    adb_tap(device, mid_x + random.randint(-10, 10), mid_y + random.randint(-10, 10))

    # === King ===
    adb_tap(device, 777 + random.randint(-7, 7), TROOP_Y + random.randint(-7, 7))
    time.sleep(random.uniform(0.15, 0.4))
    adb_tap(device, mid_x + random.randint(-10, 10), mid_y + random.randint(-10, 10))
    time.sleep(random.uniform(0.15, 0.25))
    adb_tap(device, mid_x + random.randint(-10, 10), mid_y + random.randint(-10, 10))
    time.sleep(random.uniform(0.15, 0.25))

    # === Queen ===
    adb_tap(device, 896 + random.randint(-7, 7), TROOP_Y + random.randint(-7, 7))
    time.sleep(random.uniform(0.15, 0.3))
    adb_tap(device, mid_x + random.randint(-10, 10), mid_y + random.randint(-10, 10))
    time.sleep(random.uniform(0.15, 0.3))
    adb_tap(device, mid_x + random.randint(-10, 10), mid_y + random.randint(-10, 10))
    time.sleep(random.uniform(0.15, 0.3))

    # === Warden ===
    adb_tap(device, 1039 + random.randint(-7, 7), TROOP_Y + random.randint(-7, 7))
    time.sleep(random.uniform(0.15, 0.3))
    adb_tap(device, mid_x + random.randint(-10, 10), mid_y + random.randint(-10, 10))
    time.sleep(random.uniform(0.15, 0.3))
    adb_tap(device, mid_x + random.randint(-10, 10), mid_y + random.randint(-10, 10))
    time.sleep(random.uniform(0.15, 0.3))

    # === Royal Champion ===
    adb_tap(device, 1200 + random.randint(-7, 7), TROOP_Y + random.randint(-7, 7))
    time.sleep(random.uniform(0.15, 0.3))
    adb_tap(device, mid_x + random.randint(-10, 10), mid_y + random.randint(-10, 10))
    time.sleep(random.uniform(0.15, 0.3))
    adb_tap(device, mid_x + random.randint(-10, 10), mid_y + random.randint(-10, 10))
    time.sleep(random.uniform(0.15, 0.3))

    # === Warden Again ===
    time.sleep(random.uniform(0.5, 0.8))
    adb_tap(device, 1039 + random.randint(-7, 7), TROOP_Y + random.randint(-7, 7))
    time.sleep(random.uniform(0.2, 0.4))

    # === King Again ===
    adb_tap(device, 777 + random.randint(-7, 7), TROOP_Y + random.randint(-7, 7))
    time.sleep(random.uniform(0.2, 0.4))

    # === Royal Champion Again ===
    adb_tap(device, 1200 + random.randint(-7, 7), TROOP_Y + random.randint(-7, 7))
    time.sleep(random.uniform(0.2, 0.4))

    if attack_strat == 2:
        adb_tap(device, 1654 + random.randint(-7, 7), TROOP_Y + random.randint(-7, 7))
        for x, y in [(988, 704), (791, 448), (1122, 535), (1026, 608), (1036, 360), (1351, 686)]:
            time.sleep(random.uniform(0.2, 0.4))
            adb_tap(device, x + random.randint(-7, 7), y + random.randint(-7, 7))

    elif attack_strat == 3:
        adb_tap(device, 1654 + random.randint(-7, 7), TROOP_Y + random.randint(-7, 7))
        for x, y in [(1258, 270), (1380, 483), (1408, 685), (1300, 522), (1285, 644)]:
            time.sleep(random.uniform(0.2, 0.4))
            adb_tap(device, x + random.randint(-7, 7), y + random.randint(-7, 7))

    # === Rage Sequence ===
    if attack_strat == 1:
        time.sleep(random.uniform(9, 11))
        jitter_x = random.randint(-10, 10)
        jitter_y = random.randint(-10, 10)
        adb_tap(device, *jitter_coord(1513, TROOP_Y))
        time.sleep(random.uniform(0.3, 0.6))
        adb_tap(device, COORDS["rage_fallback1"][0] + jitter_x, COORDS["rage_fallback1"][1] + jitter_y)
        time.sleep(random.uniform(0.5, 0.8))
        adb_tap(device, COORDS["rage_fallback2"][0] + jitter_x, COORDS["rage_fallback2"][1] + jitter_y)
        time.sleep(random.uniform(0.3, 0.6))
        adb_tap(device, COORDS["rage_fallback3"][0] + jitter_x, COORDS["rage_fallback3"][1] + jitter_y)
        time.sleep(random.uniform(5, 8))
        adb_tap(device, *jitter_coord(1513, TROOP_Y))
        adb_tap(device, COORDS["rage_fallback4"][0] + jitter_x, COORDS["rage_fallback4"][1] + jitter_y)
        time.sleep(random.uniform(0.5, 1))
        adb_tap(device, COORDS["rage_fallback5"][0] + jitter_x, COORDS["rage_fallback5"][1] + jitter_y)

    elif attack_strat == 2:
        time.sleep(random.uniform(15, 25))
        adb_tap(device, *jitter_coord(1513, TROOP_Y))
        for x, y in [(1013, 307), (1035, 513), (1055, 689), (1409, 477), (1421, 679)]:
            adb_tap(device, x + random.randint(-7, 7) + 15, y + random.randint(-7, 7))
            time.sleep(random.uniform(0.3, 0.6))

    elif attack_strat == 3:
        time.sleep(random.uniform(15, 25))
        adb_tap(device, *jitter_coord(1513, TROOP_Y))
        for x, y in [(1258, 270), (1380, 483), (1408, 685), (900, 400), (980, 600)]:
            adb_tap(device, x + random.randint(-7, 7) - 40, y + random.randint(-7, 7))
            time.sleep(random.uniform(0.3, 0.6))

    print(f"[{device}] Waiting 1:50 before tapping 130,800 to proceed...")
    time.sleep(110)
    adb_tap(device, 130 + random.randint(-5, 5), 800 + random.randint(-5, 5))
    time.sleep(5)
    adb_tap(device, 1400 + random.randint(-5, 5), 700 + random.randint(-5, 5))
    time.sleep(0.5)
    wait_for_template(device, "templates/return_home.png", timeout=200)


def xp_attack(device, attack_num):
    """XP mode attack: enter matchmaking, deploy siege + 4 freezes, then surrender."""
    print(f"[{device}] XP attack {attack_num}: entering matchmaking...")

    adb_tap(device, 158 + random.randint(-5, 5), 951 + random.randint(-5, 5))
    time.sleep(random.uniform(0.5, 1))
    adb_tap(device, COORDS["backup_attack"][0], COORDS["backup_attack"][1])
    time.sleep(random.uniform(0.5, 1))

    match_btn = wait_for_template(device, "templates/find_match.png", timeout=3)
    if match_btn:
        adb_tap(device, match_btn[0], match_btn[1])
    else:
        adb_tap(device, 386, 786)
    time.sleep(random.uniform(0.5, 1))

    adb_tap(device, 1900 + random.randint(-5, 5), 990 + random.randint(-5, 5))
    time.sleep(random.uniform(1, 2))

    # Wait for battle screen
    next_btn = wait_for_template(device, "templates/next_button.png", timeout=30)
    if next_btn:
        adb_tap(device, next_btn[0] + random.randint(-20, 20), next_btn[1] + random.randint(-10, 10))
        time.sleep(random.uniform(0.5, 1))

    # Wait to be in battle
    wait_for_template(device, "templates/next_button.png", timeout=20)
    time.sleep(random.uniform(0.5, 1))

    # === Siege (x=436, deploy once) ===
    print(f"[{device}] XP: deploying siege...")
    adb_tap(device, 436 + random.randint(-7, 7), 960 + random.randint(-7, 7))
    time.sleep(random.uniform(0.2, 0.4))
    adb_tap(device, 960 + random.randint(-30, 30), 400 + random.randint(-30, 30))
    time.sleep(random.uniform(0.3, 0.5))

    # === Freeze (x=1200, deploy 4 times) ===
    print(f"[{device}] XP: deploying freeze spells...")
    adb_tap(device, 1200 + random.randint(-7, 7), 960 + random.randint(-7, 7))
    time.sleep(random.uniform(0.2, 0.4))
    for _ in range(4):
        adb_tap(device, 960 + random.randint(-40, 40), 400 + random.randint(-40, 40))
        time.sleep(random.uniform(0.25, 0.4))

    # === Surrender ===
    print(f"[{device}] XP: surrendering...")
    time.sleep(random.uniform(0.5, 1))
    surrender = wait_for_template(device, "templates/surrender.png", timeout=5)
    if surrender:
        adb_tap(device, surrender[0] + random.randint(-20, 20), surrender[1] + random.randint(-10, 10))
    else:
        # Fallback surrender button coords
        adb_tap(device, 75 + random.randint(-10, 10), 800 + random.randint(-10, 10))
    time.sleep(random.uniform(0.5, 1))

    okay = wait_for_template(device, "templates/okay.png", timeout=5)
    if okay:
        adb_tap(device, okay[0] + random.randint(-20, 20), okay[1] + random.randint(-10, 10))
