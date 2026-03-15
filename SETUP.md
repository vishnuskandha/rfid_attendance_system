# Installation & Setup Guide

Complete step-by-step guide for setting up the RFID & Face Recognition Attendance System.

---

## 🖥️ System Requirements

### Hardware
- **Raspberry Pi**: Model 4B or 5 (recommended 4GB+ RAM)
- **Camera**: Raspberry Pi Camera v2 or equivalent USB camera
- **RFID Reader**: RC522 module or similar
- **Storage**: microSD 32GB (class 10 recommended)
- **Power**: 5V 3A minimum

### Optional Hardware
- Green LED + 220Ω resistor
- Red LED + 220Ω resistor
- Active Buzzer (5V)
- 16x2 I2C LCD Display
- Male-to-Female jumper wires

---

## 📋 Pre-Installation

### 1. Enable Camera
```bash
sudo raspi-config
# Navigate to: Interfacing Options > Camera > Enable
# Reboot
sudo reboot
```

### 2. Enable I2C
```bash
sudo raspi-config
# Navigate to: Interfacing Options > I2C > Enable
# Reboot
sudo reboot
```

### 3. Enable GPIO (if not automatic)
```bash
sudo raspi-config
# Navigate to: Interfacing Options > GPIO > Enable
```

### 4. Update System
```bash
sudo apt update
sudo apt upgrade -y
```

---

## 🐍 Python Environment Setup

### 1. Install Python & Dependencies
```bash
sudo apt install python3-pip python3-venv -y
sudo apt install python3-opencv python3-numpy -y
sudo apt install libatlas-base-dev libjasper-dev -y
sudo apt install libhdf5-dev libharfbuzz0b libwebp6 -y
```

### 2. Create Virtual Environment
```bash
cd /home/pi/rfid_attendance
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Python Packages
```bash
pip install --upgrade pip setuptools wheel
pip install face-recognition opencv-python numpy requests
pip install mfrc522 RPi.GPIO smbus2
pip install pandas openpyxl
```

### 4. Verify Installation
```bash
python3 -c "import cv2, face_recognition, numpy; print('✓ All packages installed')"
```

---

## 📁 Project Structure Setup

### 1. Create Directories
```bash
cd /home/pi/rfid_attendance

# Create face recognition directories
mkdir -p known_faces/srinivas
mkdir -p known_faces/manish
mkdir -p unknown_faces

# Create backup directory
mkdir -p backups
```

### 2. Add Training Images
```bash
# Copy face images to training directories
cp ~/Downloads/srinivas_1.jpg known_faces/srinivas/
cp ~/Downloads/manish_1.jpg known_faces/manish/
# ... repeat for all training images

# Requirements per person:
# - 3-5 clear images
# - Different angles/lighting
# - JPEG or PNG format
# - Face occupies 50%+ of image
```

### 3. Verify Structure
```bash
tree /home/pi/rfid_attendance
# Should show:
# ├── test.py
# ├── rfid.py
# ├── hardware.py
# ├── known_faces/
# ├── unknown_faces/
# ├── attendance.csv
# └── venv/
```

---

## ⚙️ Configuration

### 1. Add Student Details
Edit `test.py` (lines 43-46):
```python
students = {
    "srinivas": {"roll": "21CS001"},
    "manish": {"roll": "21CS002"},
    "new_name": {"roll": "21CS003"}  # Add more
}
```

### 2. Register RFID Cards
Edit `test.py` (lines 48-52):
```python
rfid_students = {
    769616991850: {"name": "Srinivas", "roll": "21CS001"},
    886622847095: {"name": "Vijay", "roll": "21CS002"},
    260401791926: {"name": "Mukesh", "roll": "21CS003"},
    # New cards:
    999888777666: {"name": "New Name", "roll": "21CS004"}
}
```

### 3. Configure Telegram
Edit `test.py` (lines 63-64):
```python
TELEGRAM_BOT_TOKEN = "123456789:ABCDEfghijklmnopqrstuvwxyz"
TELEGRAM_CHAT_ID = "1234567890"
```

**How to get Telegram token:**
1. Message [@BotFather](https://t.me/botfather) on Telegram
2. Create new bot (`/newbot`)
3. Copy the token
4. Message your bot and get Chat ID (@userinfobot)

### 4. Adjust Performance Settings
Edit `test.py` (lines 19-22):
```python
FRAME_RESIZE_SCALE = 0.5   # 0.5 = 50% of original (faster)
FACE_MATCH_THRESHOLD = 0.4 # Lower = stricter (0.4 recommended)
FRAME_SKIP = 2             # Process every 2nd frame
TELEGRAM_TIMEOUT = 3       # Seconds
```

---

## 🔌 Hardware Setup

### GPIO Pin Configuration (TESTED & WORKING ✓)
Edit `hardware.py` - Current working configuration (lines 16-22):
```python
GREEN_LED = 17     # GPIO 17 (Pin 11) - ✓ CONFIRMED WORKING
RED_LED = 27       # GPIO 27 (Pin 13) - ✓ CONFIRMED WORKING
BUZZER = 22        # GPIO 22 (Pin 15) - ✓ CONFIRMED WORKING
```

### LED Wiring
```
Green LED (GPIO 17 / Pin 11):
  - Positive (long leg) → 470Ω Resistor → GPIO 17 (Pin 11)
  - Negative (short leg) → GND

Red LED (GPIO 27 / Pin 13):
  - Positive (long leg) → 470Ω Resistor → GPIO 27 (Pin 13)
  - Negative (short leg) → GND

Buzzer (GPIO 22 / Pin 15):
  - Positive (+) → GPIO 22 (Pin 15)
  - Negative (-) → GND
```

### LCD I2C Display (TESTED & DETECTED ✓)
```
LCD Module → Raspberry Pi
VCC → Pin 2 (5V)
GND → Pin 6 (GND)
SDA → Pin 3 (GPIO 2) - ✓ WORKING
SCL → Pin 5 (GPIO 3) - ✓ WORKING
I2C Address: 0x27 (Confirmed)
```

### RFID RC522
```
RC522 → Raspberry Pi
SDA → Pin 24 (GPIO 8)
SCK → Pin 23 (GPIO 11)
MOSI → Pin 19 (GPIO 10)
MISO → Pin 21 (GPIO 9)
IRQ → Not used
GND → Pin 6 (GND)
RST → Pin 22 (GPIO 25)
3.3V → Pin 1 (3.3V)
```

---

## 🧪 Testing

### 1. Test Camera
```bash
libcamera-hello -t 5000
# Should show camera preview for 5 seconds
```

### 2. Test GPIO (LEDs & Buzzer)
```bash
cd /home/pi/rfid_attendance
source venv/bin/activate
python3 test_hardware.py
# Should test all components sequentially
```

### 3. Test I2C Devices
```bash
i2cdetect -y 1
# Should show LCD address (typically 0x27 or 0x3F)
```

### 4. Test Face Recognition
```bash
cd /home/pi/rfid_attendance
source venv/bin/activate
python3 -c "
import cv2
import face_recognition
import os

# Count loaded encodings
known_faces = 0
for person in os.listdir('known_faces'):
    for img in os.listdir(f'known_faces/{person}'):
        known_faces += 1

print(f'✓ {known_faces} training images found')

# Test camera
cap = cv2.VideoCapture(0)
ret, frame = cap.read()
cap.release()
print('✓ Camera working' if ret else '✗ Camera failed')
"
```

### 5. Test RFID Reader
```bash
cd /home/pi/rfid_attendance
source venv/bin/activate
python3 << 'EOF'
try:
    from mfrc522 import SimpleMFRC522
    reader = SimpleMFRC522()
    print("✓ RFID reader library OK")
    print("Scan a card to test...")
    id, text = reader.read()
    print(f"✓ Card detected: {id}")
except Exception as e:
    print(f"✗ RFID error: {e}")
EOF
```

---

## 🚀 First Run

### Preparation
```bash
cd /home/pi/rfid_attendance
source venv/bin/activate
```

### Check Dependencies
```bash
python3 -m py_compile test.py rfid.py hardware.py
echo "✓ All files ready"
```

### Start System
```bash
# Combined Face + RFID
python3 test.py

# Or RFID only
python3 rfid.py
```

### Expected Output
```
Loading dataset...
  ✓ srinivas loaded from srinivas.jpg
  ✓ manish loaded from manish.jpg
✓ 2 encodings loaded

✓ I2C Bus initialized
⚠ LCD not detected at 0x27 (OK if no LCD)

✓ RFID thread started

🎥 Camera started. Press 'q' to quit.

[System running - ready for faces/cards]
```

---

## 🔄 Auto-Start on Boot

### Create Service File
```bash
sudo nano /etc/systemd/system/attendance.service
```

Add this content:
```ini
[Unit]
Description=Attendance System
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/rfid_attendance
ExecStart=/home/pi/rfid_attendance/venv/bin/python3 /home/pi/rfid_attendance/test.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### Enable Service
```bash
sudo systemctl enable attendance.service
sudo systemctl start attendance.service

# Check status
sudo systemctl status attendance.service

# View logs
sudo journalctl -u attendance.service -f
```

---

## 📦 Backup & Restore

### Backup Data
```bash
# Backup attendance CSV
cp attendance.csv attendance_backup_$(date +%Y%m%d_%H%M%S).csv

# Backup unknown faces
tar -czf unknown_faces_backup_$(date +%Y%m%d_%H%M%S).tar.gz unknown_faces/

# Backup known faces (optional)
tar -czf known_faces_backup_$(date +%Y%m%d_%H%M%S).tar.gz known_faces/
```

### Restore Backup
```bash
# Restore attendance
cp attendance_backup_20260313_120000.csv attendance.csv

# Restore unknown faces
tar -xzf unknown_faces_backup_20260313_120000.tar.gz
```

---

## 🐛 Common Setup Issues

### Issue: "No module named 'face_recognition'"
**Solution:**
```bash
source venv/bin/activate
pip install face-recognition
```

### Issue: "ModuleNotFoundError: No module named 'RPi'"
**Solution:**
```bash
# This is normal on non-Pi systems - RFID/GPIO disabled automatically
# On RPi, update: pip install RPi.GPIO
```

### Issue: Camera not detected
**Solution:**
```bash
# Check camera connection
vcgencmd get_camera

# Enable camera
sudo raspi-config
# Interfacing Options > Camera > Enable

# Reboot
sudo reboot
```

### Issue: Permission denied for GPIO
**Solution:**
```bash
# Add user to gpio group
sudo usermod -a -G gpio pi

# Or run with sudo
sudo python3 test.py
```

---

## ✅ Setup Checklist

- [ ] Raspberry Pi OS installed and updated
- [ ] Camera enabled and tested
- [ ] I2C enabled (for LCD)
- [ ] GPIO enabled (for LEDs)
- [ ] Python 3.11+ installed
- [ ] Virtual environment created
- [ ] All dependencies installed
- [ ] Student details added to code
- [ ] RFID cards registered (if used)
- [ ] Training images added to `known_faces/`
- [ ] Telegram token and Chat ID configured
- [ ] Hardware connected and tested
- [ ] First run test successful
- [ ] Attendance CSV created
- [ ] (Optional) Service file enabled for auto-start

---

## 📞 Support

If issues persist:
1. Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
2. Review error messages in console
3. Test individual components with `test_hardware.py`
4. Verify all connections

---

**Last Updated**: March 13, 2026 | **Status**: ✅ Ready for Production
