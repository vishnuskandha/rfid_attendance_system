# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability in this project, please do not open a
public issue. Report it privately by opening a GitHub Security Advisory at:

https://github.com/vishnuskandha/rfid_attendance_system/security/advisories

Please include:

- A description of the vulnerability and the affected files/functions
- Steps to reproduce
- The impact of the issue

You should receive an acknowledgment within 3 business days.

## Biometric and Attendance Data Handling

This system processes biometric (face) data and stores attendance records. Treat
this data as sensitive personal information:

- **Never commit face images or attendance records to version control.** The
  `known_faces/` and `face_recognition_pi/known_faces/` directories contain
  personal photos and are excluded via `.gitignore`.
- Keep training images and `attendance.csv` on the device, or on encrypted
  storage. Back up with restricted permissions.
- Restrict access to the Raspberry Pi and its storage. Use a non-default user
  account and keep the system updated (`sudo apt update && sudo apt upgrade`).
- Rotate access regularly and audit who can read attendance data.

## Credentials

- **Telegram Bot Token** (`TELEGRAM_BOT_TOKEN`) and **Chat ID**
  (`TELEGRAM_CHAT_ID`) are read from environment variables via `.env`
  (`python-dotenv`). Never hard-code them in the source files.
- Add a `.env` file locally and keep it out of version control (it is already
  ignored). If a token is ever committed or leaked, revoke it immediately in
  BotFather and generate a new one.
- Twilio credentials (`TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`) used by
  `face_recognition_pi/face_twilio.py` are also read from the environment.

## Hardware and Privileges

- GPIO access may require root or membership in the `gpio` group. Running the
  system with `sudo` is sometimes necessary but should be limited to the
  dedicated service user when possible (see the systemd unit in `SETUP.md`).
- The RFID reader and I2C bus are directly controlled by the scripts; ensure the
  physical hardware is trusted and physically secured.

## Supported Versions

| Version | Supported          |
|---------|--------------------|
| master  | :white_check_mark: |

## Security Best Practices for Contributors

- Run `python -m py_compile` on all modified `.py` files before committing.
- Never commit `.env`, face images, CSV/XLSX attendance data, or screenshots.
- Keep third-party dependencies up to date (`face-recognition`, `opencv-python`,
  `requests`, `pandas`, `RPi.GPIO`, `mfrc522`, `smbus2`).
