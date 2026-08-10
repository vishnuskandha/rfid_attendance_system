# Contributing to RFID & Face Recognition Attendance System

Thanks for taking the time to contribute. Please read the project docs first
([README.md](README.md), [SETUP.md](SETUP.md), [USAGE.md](USAGE.md)) so changes
stay consistent with the intended Raspberry Pi deployment.

## Getting Started

1. Fork the repository and clone your fork.
2. Create a feature branch: `git checkout -b feature/your-feature`.
3. Make your changes and verify them (see below).
4. Commit with a clear message and open a pull request against `master`.

## Development Setup

This project targets a Raspberry Pi (Python 3.11+) with GPIO, I2C, camera, and
RFID hardware. Most modules require the Pi to import at runtime, but you can
still syntax-check and unit-test pure logic on any machine:

```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip setuptools wheel
pip install face-recognition opencv-python numpy requests mfrc522 RPi.GPIO smbus2 pandas openpyxl
```

## Before Submitting

- Run `python -m py_compile` on every changed `.py` file:

  ```bash
  find . -name "*.py" -print0 | xargs -0 -n1 python3 -m py_compile
  ```

- The CI workflow runs the same syntax check on every push/PR.
- Do not add or run hardware-dependent test scripts (`test_hardware.py`,
  `test_gpio_i2c.py`, `test_lcd.py`) in CI or on non-Pi machines; they require
  physical hardware.
- Keep runtime data out of the repository: never commit face images
  (`known_faces/`), `attendance.csv`, `attendance.xlsx`, `unknown_faces/`, or
  `.env` files.

## Style

- Follow the existing code style: modular functions, clear docstrings, no
  secrets in source.
- Use meaningful names and keep configuration constants grouped at the top of
  the file (e.g. `FRAME_RESIZE_SCALE`, `FACE_MATCH_THRESHOLD`).
- Update [API_REFERENCE.md](API_REFERENCE.md) when you change function
  signatures or add modules.
- Update [README.md](README.md) when behavior or setup steps change.

## Commit Messages

Use concise, descriptive messages, e.g.:

```
Fix duplicate attendance marking for late entries
```

## Pull Request Checklist

- [ ] `py_compile` passes for all changed files
- [ ] Docs updated (README / API_REFERENCE / TROUBLESHOOTING as needed)
- [ ] No credentials, face images, or runtime data added
- [ ] Behavior verified on a Raspberry Pi (if hardware is affected)

## Reporting Bugs

Open an issue with the Raspberry Pi model, OS version, and the full error
output. If it is security-related, follow [SECURITY.md](SECURITY.md).
