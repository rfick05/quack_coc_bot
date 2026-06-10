import threading
import time
import random
from adb_utils import get_devices
from modes import farm_mode, donation_mode, xp_main_mode, xp_mini_mode


def main():
    devices = get_devices()

    if not devices:
        print("No devices found.")
        return

    print("Devices:")
    for i, d in enumerate(devices):
        print(f"  {i}: {d}")

    print("\nSelect mode:")
    print("  1: Farm mode")
    print("  2: XP mode")
    print("  3: Donation mode (main only)")
    mode = input("Mode: ").strip()

    print("\nDevices:")
    for i, d in enumerate(devices):
        print(f"  {i}: {d}")
    try:
        main_idx = int(input("Which device is the main? Enter index: "))
        main_device = devices[main_idx]
    except (ValueError, IndexError):
        main_device = None
        print("No main device selected.")

    donate_signal = threading.Event()
    donate_lock = threading.Lock()
    threads = []

    if mode == "2":
        # XP mode
        for device in devices:
            is_main = (device == main_device)
            if is_main:
                t = threading.Thread(target=xp_main_mode, args=(device, donate_signal, donate_lock))
            else:
                t = threading.Thread(target=xp_mini_mode, args=(device, donate_signal, donate_lock))
            t.start()
            threads.append(t)

    elif mode == "3":
        # Donation only — main sits and donates, no farming
        t = threading.Thread(target=donation_mode, args=(main_device, 0, donate_signal, donate_lock))
        t.start()
        threads.append(t)

    else:
        # Farm mode
        print("\nFarm mode selected. Using full attack mode.")
        try:
            iterations = int(input("How many attacks? "))
        except ValueError:
            iterations = 10

        donation_enabled = input("Enable donation mode? (y/n): ").strip().lower() == "y"
        main_farms = False

        if donation_enabled and main_device:
            main_farms = input("Should main also farm? (y/n): ").strip().lower() == "y"

        for device in devices:
            is_main = donation_enabled and (device == main_device)
            if is_main:
                t = threading.Thread(
                    target=donation_mode,
                    args=(device, iterations if main_farms else 0, donate_signal, donate_lock)
                )
            else:
                t = threading.Thread(
                    target=farm_mode,
                    args=(device, iterations, donation_enabled, donate_signal, donate_lock)
                )
            t.start()
            threads.append(t)

    for t in threads:
        t.join()


if __name__ == "__main__":
    main()
