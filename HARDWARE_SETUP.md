# Hardware Integration - Attendance System

## Overview
This document describes the integrated hardware components for the RFID and Face Recognition Attendance System.

---

## Hardware Components

### 1. **LEDs**
- **Green LED (GPIO 17)**: Indicates successful registration/presence
  - Connected to **Physical Pin 11**
  - Turns ON for 1 second when registered person is detected
  - Indicates "Present" status
  
- **Red LED (GPIO 27)**: Indicates unknown/unregistered person
  - Connected to **Physical Pin 13**
  - Turns ON for 1 second when unknown person is detected
  - Indicates "Absent" or "Unknown" status

### 2. **Buzzer (GPIO 22)**
- **Connected to Physical Pin 15**
- **Registered Person**: 1 beep (0.2s duration)
- **Unknown Person**: 5 beeps (0.15s each) with gaps
- Non-blocking operation (uses threading for Telegram sends)

### 3. **LCD Display (16x2 via I2C)**
- **I2C Address**: 0x27 (default, or 0x3F if custom)
- **SDA**: GPIO 2 (Physical Pin 3)
- **SCL**: GPIO 3 (Physical Pin 5)
- **Status**: ✅ Confirmed Working

#### LCD Display Modes:
**Registered/Known Person:**
```
Line 1: "  Name"
Line 2: "Roll Status"
```

**Unknown Person:**
```
Line 1: "UNKNOWN FACE"
Line 2: "HH:MM:SS"
```

---

## System Behavior

### Face Recognition System (`test.py`)

**When Known Face Detected:**
1. ✓ Green LED turns ON for 1 second
2. ✓ Single beep sound
3. ✓ LCD displays: Name | Roll | Status
4. ✓ Data saved to CSV
5. ✓ Telegram notification sent

**When Unknown Face Detected:**
1. 🔴 Red LED turns ON for 1 second
2. 🔔 5 beep sounds
3. 🔴 LCD displays: "UNKNOWN FACE" + Time
4. 📸 Image saved to `unknown_faces/`
5. ✉️ Telegram notification sent with image

### RFID System (`rfid.py`)

**When Valid Card Scanned:**
1. ✓ Green LED turns ON for 1 second
2. ✓ Single beep sound
3. ✓ LCD displays: RFID: Name | Roll
4. ✓ Attendance marked in Excel/CSV
5. ✉️ Telegram notification sent

**When Unknown Card Scanned:**
1. 🔴 Red LED turns ON for 1 second
2. 🔔 5 beep sounds
3. ❌ LCD displays: "Unknown RFID" + "Authorization Failed"
4. ⚠️ No attendance recorded

---

## Installation & Setup

### 1. Install Required Libraries
```bash
pip install RPi.GPIO requests

# For I2C LCD support (optional):
pip install smbus2 PCF8574-library Adafruit-LCD1602
```

### 2. Enable I2C on Raspberry Pi
```bash
sudo raspi-config
# Navigate to: Interface Options > I2C > Enable
```

### 3. Verify I2C Address
```bash
i2cdetect -y 1
```
Look for your LCD module (usually `27` or `3F`)

### 4. Update I2C Address in `hardware.py` (if needed)
```python
LCD_I2C_ADDRESS = 0x27  # Change if needed
```

### 5. GPIO Pin Configuration (if using different pins)
Edit `hardware.py`:
```python
GREEN_LED = 17     # GPIO 17 (Pin 11) - Confirmed Working ✓
RED_LED = 27       # GPIO 27 (Pin 13) - Confirmed Working ✓
BUZZER = 22        # GPIO 22 (Pin 15) - Confirmed Working ✓
LCD_I2C_ADDRESS = 0x27  # LCD I2C address
```

---

## Testing Hardware

### Test Script
Run the hardware test before starting the main system:

```bash
cd /home/pi/rfid_attendance
source venv/bin/activate
python3 test_hardware.py
```

**What it tests:**
1. ✓ Green LED functionality
2. ✓ Red LED functionality
3. ✓ Buzzer functionality
4. ✓ LCD Known Face display
5. ✓ LCD Unknown Face display
6. ✓ Full registered response (LED + buzzer + LCD)
7. ✓ Full unknown response (LED + buzzer + LCD)

---

## Running the System

### Option 1: Face Recognition Only
```bash
cd /home/pi/rfid_attendance
source venv/bin/activate
python3 test.py
```

### Option 2: RFID Only
```bash
cd /home/pi/rfid_attendance
python3 rfid.py
```

### Option 3: Simultaneous (using GNU Screen/Tmux)
```bash
# Terminal 1: Face recognition
cd /home/pi/rfid_attendance && source venv/bin/activate && python3 test.py

# Terminal 2: RFID
cd /home/pi/rfid_attendance && python3 rfid.py
```

---

## Hardware Module (`hardware.py`)

The hardware module provides these functions:

### LED Control
```python
hardware.set_green_led(True, duration=1)   # Turn ON for 1 second
hardware.set_red_led(True, duration=1)     # Turn ON for 1 second
hardware.turn_off_all()                    # Turn OFF all components
```

### Buzzer Control
```python
hardware.beep(times=1, duration=0.2, interval=0.2)  # Beep N times
```

### LCD Display
```python
hardware.lcd_write(line1="Text", line2="Text")      # Write to LCD
hardware.lcd_known_face(name, roll, status)         # Display known person
hardware.lcd_unknown_face()                         # Display unknown person
```

### Response Handlers
```python
hardware.handle_registered(name, roll, status)      # Full response for known person
hardware.handle_unknown()                           # Full response for unknown person
hardware.cleanup()                                  # Clean up GPIO & LCD
```

---

## Troubleshooting

### LCD Not Displaying
1. Check I2C connection: `i2cdetect -y 1`
2. Verify I2C address matches `LSC_I2C_ADDRESS` in `hardware.py`
3. Check PCF8574 module power (GND and VCC)
4. Try address `0x3F` instead of `0x27`

### Buzzer Not Working
1. Check GPIO pin number in `hardware.py`
2. Verify buzzer polarity (+ to GPIO, - to GND)
3. Test with: `python3 test_hardware.py`

### LED Not Lighting
1. Check GPIO pin numbers
2. Verify LED polarity (short leg to GND, long leg to GPIO)
3. Check resistor value (220Ω recommended)
4. Test with: `python3 test_hardware.py`

### GPIO Already Busy Error
Solution:
```bash
# Clean up GPIO
python3 -c "import RPi.GPIO as GPIO; GPIO.setmode(GPIO.BCM); GPIO.cleanup()"

# Then restart system
python3 test.py
```

---

## I2C Wiring (LCD Module)

| LCD Pin | Raspberry Pi Pin | GPIO |
|---------|-----------------|------|
| SDA     | Pin 3           | GPIO 2 |
| SCL     | Pin 5           | GPIO 3 |
| VCC     | Pin 2/4 (5V)    | —   |
| GND     | Pin 6/9/14/20/25| —   |

---

## LED/Buzzer Wiring

### Green LED
- Positive → GPIO 2
- Negative → 220Ω Resistor → GND

### Red LED
- Positive → GPIO 3
- Negative → 220Ω Resistor → GND

### Buzzer (Active)
- Positive → GPIO 4
- Negative → GND

---

## Environment Variables (Optional)

Set Telegram credentials via environment variables to keep them secure:

```bash
export TELEGRAM_BOT_TOKEN="your_bot_token_here"
export TELEGRAM_CHAT_ID="your_chat_id_here"
```

Or use in scripts:
```python
import os
bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
chat_id = os.getenv('TELEGRAM_CHAT_ID')
```

---

## Support

For issues or questions regarding hardware integration:

1. Run `python3 test_hardware.py` to diagnose problems
2. Check GPIO pin configuration matches your setup
3. Verify I2C address with `i2cdetect -y 1`
4. Review `hardware.py` for available functions and configurations

---

**Last Updated**: March 13, 2026
**System**: Raspberry Pi with Face Recognition + RFID Attendance
