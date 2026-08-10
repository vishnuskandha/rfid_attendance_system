# RFID & Face Recognition Attendance System

[![CI](https://github.com/vishnuskandha/rfid_attendance_system/actions/workflows/ci.yml/badge.svg)](https://github.com/vishnuskandha/rfid_attendance_system/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)

An attendance management system for the Raspberry Pi that combines RFID card
scanning with real-time face recognition, wired to LED/buzzer/LCD hardware
feedback and Telegram notifications.

## Overview

- **Face recognition** through a live camera feed using the `face_recognition`
  library, matching detected faces against locally stored training images.
- **RFID card scanning** through an RC522/MFRC522 reader running in a parallel
  thread.
- **Attendance logging** to CSV (combined system) or Excel (RFID-only mode)
  with duplicate prevention and time-based `Present`/`Absent` status.
- **Hardware feedback** - green/red LEDs, buzzer, and a 16x2 I2C LCD.
- **Telegram alerts** for known and unknown faces/cards, sent asynchronously.

## System Architecture

```
rfid_attendance_system/
├── test.py                  # Main system: face recognition + RFID (entry point)
├── rfid.py                  # Standalone RFID-only attendance system
├── hardware.py              # GPIO (LED/buzzer) and I2C LCD control
├── face.py                  # Pi-camera face door auth demo
├── face_recognition_pi/     # Older standalone Pi face-auth demos (keypad, Twilio)
│   ├── face.py
│   ├── face_twilio.py
│   ├── facerecognition.py
│   └── test.py
├── test_hardware.py         # Hardware test utility (LED/buzzer/LCD)
├── test_gpio_i2c.py         # GPIO/I2C pin test utility
├── test_lcd.py              # LCD/I2C test utility
├── known_faces/             # Local training data - NOT committed (see below)
├── unknown_faces/           # Generated at runtime - unknown face captures
├── attendance.csv           # Generated at runtime - attendance records
└── docs (.md)               # Full documentation set (see table below)
```

Two independent detection paths feed one attendance log:

1. **Camera path** - captures frames, resizes/skips for speed, detects faces,
   compares against encoded training data, and marks attendance.
2. **RFID path** - runs in a background thread, reads card IDs, matches against
   the registered-card table, and marks attendance.

Both paths share hardware feedback and Telegram notification helpers.

### Face Training Data

`known_faces/` and `face_recognition_pi/known_faces/` are **local personal data
and are excluded from version control** (`.gitignore`). Create one subdirectory
per person, place 3-5 clear JPEG/PNG photos in each, and add the person to the
`students` dictionary in `test.py`:

```
known_faces/
├── srinivas/
│   ├── srinivas.jpg
│   └── srinivas_1.jpg
└── manish/
    ├── manish.jpg
    └── manish_1.jpg
```

## Quick Start

1. **Setup** - enable camera/I2C/GPIO and install dependencies. See
   [SETUP.md](SETUP.md).
2. **Configure** - add students, register RFID cards, and set Telegram
   credentials in `test.py`. See [USAGE.md](USAGE.md).
3. **Reference** - the essential commands are in
   [QUICK_REFERENCE.md](QUICK_REFERENCE.md).

Then run:

```bash
# Combined face + RFID system
python3 test.py

# RFID only
python3 rfid.py
```

## Features

| Area | Capability |
|------|------------|
| Face recognition | Real-time detection and identification, HOG model, frame skip + resize for speed |
| RFID | RC522/MFRC522 scanning in a background thread, per-minute duplicate prevention |
| Attendance status | `Present` (<= 09:00), `Absent` (> 09:00); cut-off configurable |
| Logging | CSV (`attendance.csv`) or Excel (`attendance.xlsx`), one row per person per day |
| Hardware | Green LED (registered), red LED (unknown), buzzer patterns, 16x2 I2C LCD |
| Notifications | Telegram messages with images for unknown faces (async, non-blocking) |
| Unknown face capture | Saves `unknown_YYYYMMDD_HHMMSS_N.jpg` into `unknown_faces/` |

## Configuration Highlights

All settings live at the top of `test.py`:

```python
FRAME_RESIZE_SCALE = 0.5     # Resize frames to 50% for faster processing
FACE_MATCH_THRESHOLD = 0.4   # Lower = stricter matching
FRAME_SKIP = 2               # Process every Nth frame
TELEGRAM_TIMEOUT = 3         # Telegram request timeout (seconds)
```

Telegram credentials are loaded from the environment (`.env`) via
`python-dotenv` - do not hard-code tokens. The attendance cut-off time and LCD
I2C address are configured in `hardware.py`.

## GPIO Pin Reference

| Component | GPIO | Physical Pin |
|-----------|------|--------------|
| Green LED | 17   | 11           |
| Red LED   | 27   | 13           |
| Buzzer    | 22   | 15           |
| LCD SDA   | 2    | 3            |
| LCD SCL   | 3    | 5            |
| LCD I2C address | - | 0x27 (or 0x3F) |

See [PIN_REFERENCE.md](PIN_REFERENCE.md) and
[HARDWARE_SETUP.md](HARDWARE_SETUP.md) for the full wiring guide.

## Documentation

| Document | Contents |
|----------|----------|
| [SETUP.md](SETUP.md) | Full installation and configuration guide |
| [USAGE.md](USAGE.md) | Operating modes, adding people/cards, monitoring |
| [QUICK_REFERENCE.md](QUICK_REFERENCE.md) | Essential commands at a glance |
| [HARDWARE_SETUP.md](HARDWARE_SETUP.md) | Wiring and hardware integration |
| [HARDWARE_STATUS.md](HARDWARE_STATUS.md) | Verified working pin configuration |
| [PIN_REFERENCE.md](PIN_REFERENCE.md) | GPIO pin cheat sheet |
| [API_REFERENCE.md](API_REFERENCE.md) | Function and module documentation |
| [TROUBLESHOOTING.md](TROUBLESHOOTING.md) | Common issues and fixes |

## Testing

This project runs on Raspberry Pi hardware; the test utilities require physical
devices:

```bash
python3 -m py_compile test.py rfid.py hardware.py face.py
python3 test_hardware.py    # LED, buzzer, LCD test (Pi only)
python3 test_lcd.py         # LCD/I2C test (Pi only)
python3 test_gpio_i2c.py    # GPIO pin test (Pi only)
```

CI runs a syntax check (`py_compile`) on every commit and pull request.

## Security

- Keep face images, attendance records, and credentials private; see
  [SECURITY.md](SECURITY.md) for details.
- Never commit `.env`, `known_faces/`, or runtime data files.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for the contribution workflow and
checklist.

## License

MIT License - see [LICENSE](LICENSE). Copyright (c) 2026 Vishnu Skandha.
