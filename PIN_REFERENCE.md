# 🎯 QUICK PIN REFERENCE - WORKING CONFIGURATION

**Last Updated:** March 14, 2026 ✅

---

## GPIO PIN CHEAT SHEET

### Attendance System Hardware

```
┌─────────────────────────────────────────┐
│     RASPBERRY PI GPIO PIN LAYOUT         │
├─────────────────────────────────────────┤
│  Physical  │  GPIO  │  Component        │
│    Pin     │  #     │  Status           │
├─────────────────────────────────────────┤
│    11      │  17    │ 🟢 GREEN LED ✅   │
│    13      │  27    │ 🔴 RED LED ✅     │
│    15      │  22    │ 🔊 BUZZER ✅      │
│     3      │   2    │ LCD SDA ✅        │
│     5      │   3    │ LCD SCL ✅        │
│     6      │  GND   │ GROUND            │
│    2,4     │ +5V    │ POWER             │
└─────────────────────────────────────────┘
```

---

## HARDWARE CONNECTIONS

### LEDs (470Ω Resistors)
```
Green LED (Pin 11):
  Anode → 470Ω → GPIO 17
  Cathode → GND

Red LED (Pin 13):
  Anode → 470Ω → GPIO 27
  Cathode → GND
```

### Buzzer (GPIO 22 / Pin 15)
```
+ (Red) → GPIO 22
- (Black) → GND
```

### LCD Display (I2C)
```
VCC → Pin 2 (+5V)
GND → Pin 6 (GND)
SDA → Pin 3 (GPIO 2)
SCL → Pin 5 (GPIO 3)
Address: 0x27
```

### RFID RC522 (SPI)
```
SDA → GPIO 8 (Pin 24)
SCK → GPIO 11 (Pin 23)
MOSI → GPIO 10 (Pin 19)
MISO → GPIO 9 (Pin 21)
RST → GPIO 25 (Pin 22)
GND → Pin 6 (GND)
3.3V → Pin 1 (3.3V)
```

---

## CODE CONFIGURATION

### hardware.py
```python
# Lines 16-22: GPIO Pin Numbers (TESTED ✅)
GREEN_LED = 17      # Pin 11
RED_LED = 27        # Pin 13
BUZZER = 22         # Pin 15

# Line 26: LCD I2C Address (DETECTED ✅)
LCD_I2C_ADDRESS = 0x27
```

---

## VERIFY HARDWARE

### Test LEDs & Buzzer
```bash
cd /home/pi/rfid_attendance
sudo python3 test_hardware.py
```

### Test GPIO Pins
```bash
sudo python3 test_gpio_i2c.py
```

### Test LCD
```bash
sudo python3 test_lcd.py
```

### Scan I2C Devices
```bash
i2cdetect -y 1
```

---

## RUN SYSTEM

### Combined Face + RFID
```bash
cd /home/pi/rfid_attendance
source venv/bin/activate
python3 test.py
```

### RFID Only
```bash
python3 rfid.py
```

---

## EXPECTED OUTPUT

### ✅ Known Person
- 🟢 Green LED ON (1 sec)
- 🔊 1 beep
- 📺 LCD: Name | Roll | Status

### ❌ Unknown Person
- 🔴 Red LED ON (1 sec)
- 🔊 5 beeps
- 📺 LCD: UNKNOWN FACE | Time

### 📱 RFID Card
- 🟢 Green LED ON (1 sec)
- 🔊 1 beep
- 📺 LCD: RFID: Name | Roll

---

## EMERGENCY STOP

```bash
# Kill running process
pkill -f python3

# Or stop specific service
ps aux | grep python
kill -9 <PID>
```

---

## STATUS

| Component | GPIO | Status |
|-----------|------|--------|
| Green LED | 17 | ✅ WORKING |
| Red LED | 27 | ✅ WORKING |
| Buzzer | 22 | ✅ WORKING |
| LCD SDA | 2 | ✅ WORKING |
| LCD SCL | 3 | ✅ WORKING |
| LCD I2C | 0x27 | ✅ DETECTED |

**All systems operational! 🎉**
