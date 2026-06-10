import time
import random
import threading
from game_actions import find_attack
from adb_utils import adb_tap
from image_utils import wait_for_template

# Mini request coords (opens clan chat to request troops)
REQUEST_COORDS = [
    (90, 482),
    (643, 1022),
    (1397, 742),
    (789, 404),
]

# Main donation coords
DONATE_COORDS = [
    (90, 482),
    (582, 896),
    (118, 742),
    (1395, 738),
    (2029, 696),
    (780, 404),
]


def request_troops(device, donate_signal, donate_lock):
    print(f"[{device}] Waiting for donation lock...")
    with donate_lock:
        print(f"[{device}] Requesting troops...")
        for x, y in REQUEST_COORDS:
            adb_tap(device, x, y)
            time.sleep(random.uniform(0.3, 0.6))
        donate_signal.set()
        time.sleep(3)
        donate_signal.clear()


def donate_troops(device):
    print(f"[{device}] Donating troops...")
    for x, y in DONATE_COORDS:
        adb_tap(device, 960 + random.randint(-20, 20), 540 + random.randint(-20, 20))
        time.sleep(random.uniform(0.2, 0.4))
        adb_tap(device, int(x), int(y))
        time.sleep(random.uniform(0.4, 0.7))
    print(f"[{device}] Donation complete.")


def donation_mode(device, iterations, donate_signal, donate_lock):
    """Main device: listens for donate signals, optionally farms too."""
    print(f"[{device}] Main device started. {'Also farming.' if iterations > 0 else 'Donation-only.'}")

    if iterations > 0:
        farm_thread = threading.Thread(
            target=farm_mode,
            args=(device, iterations, True, donate_signal, donate_lock),
            daemon=True
        )
        farm_thread.start()

        while farm_thread.is_alive():
            if donate_signal.wait(timeout=1):
                donate_troops(device)
                donate_signal.clear()
        farm_thread.join()
    else:
        while True:
            donate_signal.wait()
            donate_troops(device)
            donate_signal.clear()


def farm_mode(device, iterations, donation_enabled, donate_signal=None, donate_lock=None):
    print(f"[{device}] Starting farm mode: {iterations} attacks, full attack")

    for i in range(iterations):
        print(f"[{device}] Attack {i + 1}/{iterations}")

        if donation_enabled and donate_signal is not None and donate_lock is not None:
            request_troops(device, donate_signal, donate_lock)

        find_attack(device)

        print(f"[{device}] Waiting for return home...")
        timeout = 180
        start_time = time.time()
        while time.time() - start_time < timeout:
            ret_home = wait_for_template(device, "templates/return_home.png", timeout=3)
            if ret_home:
                print(f"[{device}] Return home detected at:", ret_home)
                time.sleep(random.uniform(0.1, 0.5))
                for _ in range(2):
                    adb_tap(device,
                            ret_home[0] + random.randint(-50, 50),
                            ret_home[1] + random.randint(-50, 50))
                    time.sleep(random.uniform(0.2, 0.3))
                time.sleep(random.uniform(0.5, 1))
                time.sleep(random.uniform(2, 5))
                break
            time.sleep(1)
        else:
            print(f"[{device}] Timeout waiting for return home.")

    print(f"[{device}] Farm mode complete.")


# XP mode donate coords for main
XP_DONATE_COORDS = [
    (844, 320, 12),   # tap 12 times
    (844, 491, 2),    # tap 2 times
    (844, 749, 4),    # tap 4 times
]


def xp_donate(device):
    """Main account: find donate button via template or fallback, then donate."""
    print(f"[{device}] XP donate: looking for donate button...")
    donate_btn = wait_for_template(device, "templates/donate_button.png", timeout=5)
    if donate_btn:
        print(f"[{device}] Found donate button at: {donate_btn}")
        adb_tap(device, donate_btn[0], donate_btn[1])
    else:
        print(f"[{device}] Donate button not found, using fallback (570, 880)")
        adb_tap(device, 570, 880)
    time.sleep(random.uniform(0.4, 0.7))

    for x, y, count in XP_DONATE_COORDS:
        for _ in range(count):
            adb_tap(device, x + random.randint(-8, 8), y + random.randint(-8, 8))
            time.sleep(random.uniform(0.2, 0.35))

    print(f"[{device}] XP donation complete.")


def xp_main_mode(device, donate_signal, donate_lock):
    """Main account in XP mode: just listens and donates indefinitely."""
    print(f"[{device}] XP main mode started, waiting for donation signals...")
    while True:
        donate_signal.wait()
        xp_donate(device)
        donate_signal.clear()


def xp_mini_mode(device, donate_signal, donate_lock):
    """Mini account in XP mode: timer -> attack x2 -> surrender -> wait -> request -> repeat."""
    from game_actions import xp_attack
    print(f"[{device}] XP mini mode started.")

    while True:
        # Start 10 minute timer (random taps to avoid AFK)
        print(f"[{device}] XP: waiting 10 minutes...")
        timer_end = time.time() + 600
        while time.time() < timer_end:
            remaining = timer_end - time.time()
            sleep_time = min(random.uniform(20, 40), remaining)
            if sleep_time > 0:
                time.sleep(sleep_time)
            if time.time() < timer_end:
                # Anti-AFK tap in safe area
                adb_tap(device, 960 + random.randint(-30, 30), 400 + random.randint(-30, 30))

        # Do two XP attacks (one per siege machine)
        for attack_num in range(1, 3):
            print(f"[{device}] XP attack {attack_num}/2")
            xp_attack(device, attack_num)

            # Wait for return home
            print(f"[{device}] Waiting for return home...")
            start = time.time()
            while time.time() - start < 120:
                ret_home = wait_for_template(device, "templates/return_home.png", timeout=3)
                if ret_home:
                    print(f"[{device}] Return home detected.")
                    adb_tap(device,
                            ret_home[0] + random.randint(-30, 30),
                            ret_home[1] + random.randint(-30, 30))
                    time.sleep(random.uniform(0.5, 1))
                    break
                time.sleep(1)

        # Request troops from main
        print(f"[{device}] XP: requesting troops...")
        request_troops(device, donate_signal, donate_lock)
