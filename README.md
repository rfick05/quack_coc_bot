# quack_coc_bot

A multi-device Clash of Clans automation bot built in Python using ADB (Android Debug Bridge) and computer vision. Designed to run farm attacks across multiple emulator instances simultaneously via multithreading.

## Features

- **Multi-device support** — detects all connected ADB devices and runs a bot thread on each in parallel
- **Template matching** — uses OpenCV to detect on-screen UI elements (attack buttons, match found screen, return home, etc.) rather than hardcoded timing
- **OCR trophy reading** — uses Tesseract to read trophy count from a configurable screen region
- **Randomized jitter** — all taps and swipes include randomized pixel offsets to simulate human input and avoid detection
- **Automated attack sequence** — handles full attack loop: navigate to matchmaking, deploy troops, trigger hero abilities and spells, wait for battle end, return home
- **Multiple deploy strategies** — randomizes troop drop coordinates across 3 diagonal drop patterns per attack

## Tech Stack

- Python 3
- [ADB (Android Debug Bridge)](https://developer.android.com/tools/adb) — device communication
- [OpenCV](https://opencv.org/) — screen capture and template matching
- [Pytesseract](https://github.com/madmaze/pytesseract) — OCR for trophy reading
- NumPy — image array processing
- Threading — parallel execution across devices

## Project Structure

```
quack_coc_bot/
├── src/
│   ├── main.py           # Entry point; spawns one thread per device
│   ├── modes.py          # Farm mode loop
│   ├── attack.py         # Full attack sequence logic
│   ├── game_actions.py   # GameActions class wrapping attack entry point
│   ├── adb_utils.py      # ADB device detection, tap, swipe, screen capture
│   ├── image_utils.py    # Template matching, wait_for_template, OCR
│   ├── coordinates.py    # Hardcoded fallback coords and troop slot positions
│   └── templates/        # PNG reference images for UI element detection
├── start.sh              # Restarts ADB server and launches bot
└── config.json           # Trophy ROI config (not included, see setup)
```

## Setup

### Requirements

- Python 3.x
- ADB installed and in PATH
- Android emulator(s) running Clash of Clans (e.g. BlueStacks)

### Install dependencies

```bash
pip install opencv-python pytesseract numpy
```

Tesseract must also be installed separately:
- Windows: [UB-Mannheim installer](https://github.com/UB-Mannheim/tesseract/wiki)
- Linux: `sudo apt install tesseract-ocr`

### config.json

Create a `config.json` in the project root with a trophy ROI:

```json
{
  "trophy_roi": {
    "x1": 100,
    "y1": 50,
    "x2": 300,
    "y2": 100
  }
}
```

Adjust the region to match where trophies appear on your emulator resolution.

## Usage

```bash
bash start.sh
```

Or manually:

```bash
adb kill-server && adb start-server
cd src
python3 main.py
```

When prompted, enter the number of attacks to run per device. The bot will detect all connected ADB devices and run farm mode on each simultaneously.

## Notes

- Attack coordinates are tuned for a specific emulator resolution. You may need to adjust `coordinates.py` and the drop coord math in `attack.py` for different screen sizes.
- Troop deploy order is hardcoded for a Siege / Electro Titan / Yeti composition with all four heroes.
- This project was built for a programming course as a practical application of computer vision, automation, and multithreading concepts.
