# Troubleshooting Guide

Common issues and solutions for the RFID & Face Recognition Attendance System.

---

## 🎥 Camera Issues

### Issue: Camera not detected
**Error:** `Cannot open camera` or blank screen

**Solutions:**
```bash
# Check camera connection
vcgencmd get_camera
# Output should be: supported=1 detected=1

# Enable camera interface
sudo raspi-config
# Interfacing Options > Camera > Enable > Reboot

# Test camera
libcamera-hello -t 5000

# Check permissions
sudo usermod -a -G video pi

# Or run with sudo
sudo python3 test.py
```

---

### Issue: Low resolution or blurry
**Error:** Faces too small or blurry in frame

**Solutions:**
```python
# In test.py, improve camera settings:
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)    # Increase resolution
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
cap.set(cv2.CAP_PROP_BRIGHTNESS, 0.5)      # Adjust brightness
cap.set(cv2.CAP_PROP_CONTRAST, 0.5)        # Adjust contrast
```

**Alternative:**
- Clean camera lens
- Improve lighting conditions
- Position camera closer to subjects

---

### Issue: Poor lighting/dark image
**Solutions:**
```python
# Increase exposure
cap.set(cv2.CAP_PROP_EXPOSURE, 0.7)

# Use USB camera with built-in light
# Or add external lighting
```

---

### Issue: Camera freezes during operation
**Solutions:**
```bash
# Increase GPU memory
sudo raspi-config
# Advanced Options > GPU Memory > 128 > Reboot

# Kill frozen processes
pkill -9 python3

# Check for USB errors
dmesg | tail -20
```

---

## 👤 Face Recognition Issues

### Issue: Face not recognized (False Negatives)
**Problem:** Known person not detected

**Solutions:**

1. **Add more training images:**
   ```bash
   mkdir -p known_faces/person_name
   cp image1.jpg known_faces/person_name/
   cp image2.jpg known_faces/person_name/
   # Add 5+ images total
   ```

2. **Improve training image quality:**
   - Use clear, well-lit photos
   - Capture multiple angles
   - Different backgrounds
   - Varied expressions

3. **Adjust matching threshold:**
   ```python
   # In test.py, make stricter:
   FACE_MATCH_THRESHOLD = 0.35  # Default 0.4, lower = stricter
   
   # For looser matching:
   FACE_MATCH_THRESHOLD = 0.50  # Higher = more lenient
   ```

4. **Check encoding quality:**
   ```bash
   python3 << 'EOF'
   import face_recognition
   image = face_recognition.load_image_file('known_faces/person/image.jpg')
   encodings = face_recognition.face_encodings(image)
   print(f"Faces found: {len(encodings)}")
   if len(encodings) == 0:
       print("No faces detected - improve image quality")
   EOF
   ```

---

### Issue: False positives (Wrong people identified)
**Problem:** Unknown person identified as someone else

**Solutions:**

1. **Stricter threshold:**
   ```python
   # In test.py:
   FACE_MATCH_THRESHOLD = 0.35  # Make more strict
   ```

2. **Improve training data:**
   - Remove poor quality images
   - Ensure diverse angles for each person
   - Avoid similar-looking people close together

3. **Increase distance check:**
   ```python
   # In test.py, near face detection:
   if best_distance < 0.35:  # Lower = stricter match
       name = known_face_names[best_match_idx]
   ```

---

### Issue: Slow face recognition
**Problem:** Processing takes too long

**Solutions:**

1. **Reduce frame size:**
   ```python
   # In test.py:
   FRAME_RESIZE_SCALE = 0.25  # Instead of 0.5 (faster)
   ```

2. **Skip more frames:**
   ```python
   FRAME_SKIP = 3  # Process every 3rd frame instead of 2nd
   ```

3. **Use faster detection model:**
   ```python
   # In test.py, change from CNN to HOG:
   face_locations = face_recognition.face_locations(
       rgb_small, 
       model="hog"  # Faster but less accurate
   )
   ```

4. **Increase GPU memory:**
   ```bash
   sudo raspi-config
   # Advanced Options > GPU Memory > 256 MB
   ```

---

## 🃏 RFID Issues

### Issue: RFID reader not detected
**Error:** `ModuleNotFoundError: No module named 'mfrc522'`

**Solutions:**
```bash
# Install RFID library
pip install mfrc522 RPi.GPIO

# Check GPIO permissions
sudo usermod -a -G gpio pi

# Test RFID independently
python3 rfid.py
```

---

### Issue: Card not scanning
**Error:** `KeyboardInterrupt` or `No data received`

**Solutions:**

1. **Check RC522 wiring:**
   ```
   RC522 → RPi
   SDA   → GPIO 8 (Pin 24)
   SCK   → GPIO 11 (Pin 23)
   MOSI  → GPIO 10 (Pin 19)
   MISO  → GPIO 9 (Pin 21)
   IRQ   → Not used
   GND   → Pin 6 (GND)
   RST   → GPIO 25 (Pin 22)
   3.3V  → Pin 1 (3.3V)
   ```

2. **Verify SPI enabled:**
   ```bash
   sudo raspi-config
   # Interfacing Options > SPI > Enable
   ```

3. **Check RC522 connection:**
   ```bash
   sudo python3 << 'EOF'
   import RPi.GPIO as GPIO
   GPIO.setmode(GPIO.BCM)
   GPIO.setwarnings(False)
   
   from mfrc522 import SimpleMFRC522
   reader = SimpleMFRC522()
   print("✓ RC522 initialized")
   print("Scan a card...")
   try:
       id, text = reader.read()
       print(f"✓ Card read: {id}")
   except:
       print("✗ Failed to read card")
   EOF
   ```

---

### Issue: Card ID not recognized
**Error:** "Unknown Card!" message

**Solutions:**

1. **Get card ID:**
   ```bash
   python3 rfid.py
   # Note the "Unknown Card!" ID printed
   ```

2. **Register card in test.py:**
   ```python
   rfid_students = {
       769616991850: {"name": "Srinivas", "roll": "21CS001"},
       999888777666: {"name": "New Person", "roll": "21CS002"}  # Add here
   }
   ```

3. **Restart system:**
   ```bash
   python3 test.py
   ```

---

### Issue: Duplicate readings
**Problem:** Same card marked multiple times

**Solution:** System prevents duplicates per minute automatically. If still occurring:
```python
# In test.py, edit rfid_thread_function:
minute_key = datetime.now().strftime("%H:%M")  # Change to hour
minute_key = datetime.now().strftime("%H")     # Per hour instead
```

---

## 💾 Data & CSV Issues

### Issue: CSV file corrupted
**Error:** Cannot open attendance.csv

**Solutions:**
```bash
# Backup corrupted file
mv attendance.csv attendance.csv.bak

# Create fresh CSV
cd /home/pi/rfid_attendance
source venv/bin/activate
python3 << 'EOF'
import csv
with open('attendance.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['Date', 'Name', 'Roll Number', 'Time', 'Status'])
print("✓ CSV recreated")
EOF
```

---

### Issue: Attendance not saving
**Error:** CSV file empty or not updating

**Solutions:**

1. **Check file permissions:**
   ```bash
   chmod 666 attendance.csv
   ```

2. **Verify write access:**
   ```bash
   touch attendance.csv
   ls -la attendance.csv  # Should show write permission
   ```

3. **Check storage space:**
   ```bash
   df -h  # Check available disk space
   ```

4. **Test CSV writing:**
   ```bash
   python3 << 'EOF'
   import csv
   from datetime import datetime
   
   with open('attendance.csv', 'a', newline='') as f:
       writer = csv.writer(f)
       writer.writerow([
           datetime.now().strftime("%Y-%m-%d"),
           "TEST", "TEST001",
           datetime.now().strftime("%H:%M:%S"),
           "Present"
       ])
   print("✓ CSV write successful")
   EOF
   ```

---

## 📱 LCD Display Issues (RESOLVED ✓)

### Status: ✅ LCD I2C Display DETECTED & WORKING
**I2C Address:** 0x27 (Confirmed)
**SDA/SCL:** GPIO 2 & GPIO 3 (Tested & Working)

### LCD Connection Verified:
```bash
i2cdetect -y 1
# Shows device at 0x27
```

### LCD Wiring (CONFIRMED WORKING):
```
LCD → RPi
VCC → Pin 2 (5V)
GND → Pin 6 (GND)
SDA → Pin 3 (GPIO 2) ✓ TESTED
SCL → Pin 5 (GPIO 3) ✓ TESTED
```

### LCD Display Output Examples:
**Known Face:**
```
  Srinivas
21CS001 Present
```

**Unknown Face:**
```
UNKNOWN FACE
14:30:45
```

**Registered RFID:**
```
RFID: Vijay
21CS002
```

### If LCD Still Not Showing Text:
1. **Check LCD address:**
   ```bash
   sudo i2cdetect -y 1
   ```

2. **Try alternative address:**
   ```python
   # In hardware.py:
   LCD_I2C_ADDRESS = 0x3F  # Try if 0x27 fails
   ```

3. **Adjust LCD contrast knob:**
   - Turn the potentiometer on the LCD module until text appears

4. **Verify pull-up resistors:**
   - Add 4.7kΩ resistors between SDA-VCC and SCL-VCC if needed
   ```

---

### Issue: LCD shows garbage characters
**Solutions:**
```python
# In hardware.py, adjust contrast/brightness:
# (Usually set via potentiometer on LCD module)

# Or reinitialize LCD:
python3 << 'EOF'
import hardware
if hardware.lcd:
    hardware.lcd_write("Hello", "World")
else:
    print("LCD not available")
EOF
```

---

## 🔌 GPIO/Hardware Issues

### Issue: LEDs not lighting up (RESOLVED ✓)
**Status:** ✅ GPIO pins 17, 27 tested and working

**Correct Configuration:**
```python
# In hardware.py (tested and working):
GREEN_LED = 17  # GPIO 17 (Pin 11) [ACTIVE]
RED_LED = 27    # GPIO 27 (Pin 13) [ACTIVE]
BUZZER = 22     # GPIO 22 (Pin 15) [ACTIVE]
```

**Wiring (CONFIRMED):**
```bash
Green LED (GPIO 17 - Pin 11):
  LED+ → 470Ω resistor → GPIO 17
  LED- → GND

Red LED (GPIO 27 - Pin 13):
  LED+ → 470Ω resistor → GPIO 27
  LED- → GND

Buzzer (GPIO 22 - Pin 15):
  + → GPIO 22
  - → GND
```

**Test GPIO:**
```bash
python3 << 'EOF'
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)

# Test Green LED (GPIO 17)
GPIO.setup(17, GPIO.OUT)
GPIO.output(17, True)
print("✓ GPIO 17 ON (Green LED should light)")

import time
time.sleep(2)
GPIO.output(17, False)
print("✓ GPIO 17 OFF")

# Test Red LED (GPIO 27)
GPIO.setup(27, GPIO.OUT)
GPIO.output(27, True)
print("✓ GPIO 27 ON (Red LED should light)")
time.sleep(2)
GPIO.output(27, False)
print("✓ GPIO 27 OFF")

GPIO.cleanup()
EOF
```

---

### Issue: Buzzer not working (RESOLVED ✓)
**Status:** ✅ GPIO 22 tested and working

**Correct GPIO:**
```python
# In hardware.py (tested and working):
BUZZER = 22  # GPIO 22 (Pin 15) [ACTIVE]
```

**Wiring:**
```bash
Active buzzer:
+ → GPIO 22 (Pin 15)
- → GND
```

**Test buzzer:**
```bash
python3 << 'EOF'
import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setup(22, GPIO.OUT)

for i in range(5):
    GPIO.output(22, True)
    time.sleep(0.2)
    GPIO.output(22, False)
    time.sleep(0.2)

print("✓ Buzzer test complete (should have beeped 5 times)")
GPIO.cleanup()
EOF
```
   GPIO.cleanup()
   EOF
   ```

---

### Issue: "GPIO is already in use"
**Error:** `RuntimeError: This channel is already in use`

**Solutions:**
```bash
# Reset GPIO
python3 << 'EOF'
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
GPIO.cleanup()
print("✓ GPIO reset")
EOF

# Kill running processes
pkill -9 python3

# Reboot
sudo reboot
```

---

## 📲 Telegram Issues

### Issue: Notifications not sending
**Error:** No Telegram messages received

**Solutions:**

1. **Verify credentials:**
   ```python
   # In test.py:
   TELEGRAM_BOT_TOKEN = "your_token_here"
   TELEGRAM_CHAT_ID = "your_chat_id_here"
   # Bot token should start with numbers
   # Chat ID should be all digits
   ```

2. **Get correct credentials:**
   - Bot token: From @BotFather
   - Chat ID: From @userinfobot

3. **Test connectivity:**
   ```bash
   python3 << 'EOF'
   import requests
   token = "YOUR_TOKEN"
   chat_id = "YOUR_CHAT_ID"
   
   url = f"https://api.telegram.org/bot{token}/sendMessage"
   payload = {"chat_id": chat_id, "text": "Test message"}
   
   try:
       resp = requests.post(url, json=payload, timeout=5)
       if resp.status_code == 200:
           print("✓ Telegram working")
       else:
           print(f"✗ Error: {resp.text}")
   except Exception as e:
       print(f"✗ Connection error: {e}")
   EOF
   ```

4. **Check internet connection:**
   ```bash
   ping -c 3 google.com
   # Should show responses
   ```

---

## ⚙️ System Performance Issues

### Issue: High CPU usage
**Solutions:**
```python
# Reduce processing load in test.py:
FRAME_RESIZE_SCALE = 0.25    # Smaller frames
FRAME_SKIP = 4               # Skip more frames
FACE_MATCH_THRESHOLD = 0.3   # Faster matching
```

---

### Issue: High memory usage
**Solutions:**
```bash
# Increase available memory
sudo raspi-config
# Advanced Options > GPU Memory > 128 MB

# Monitor memory
free -h

# Kill unused processes
ps aux | grep python
pkill -f unused_process
```

---

### Issue: No space left on device
**Solutions:**
```bash
# Check disk space
df -h

# Clean unnecessary files
rm -rf ~/Downloads/*
rm -rf ~/.cache/*

# Archive old unknown faces
tar -czf unknown_faces_old.tar.gz unknown_faces/
rm -rf unknown_faces/*

# Move to external drive
scp attendance.csv user@remote:/backup/
```

---

## 🔄 Startup/Restart Issues

### Issue: System crashes on startup
**Solutions:**

1. **Check for errors:**
   ```bash
   python3 test.py 2>&1 | head -50
   ```

2. **Verify all imports:**
   ```bash
   source venv/bin/activate
   python3 -c "import cv2, face_recognition, RPi.GPIO; print('✓ OK')"
   ```

3. **Check dataset:**
   ```bash
   ls -la known_faces/
   # Should contain subdirectories with images
   ```

4. **Reboot system:**
   ```bash
   sudo reboot
   ```

---

### Issue: Service not auto-starting
**Solutions:**
```bash
# Check service status
sudo systemctl status attendance.service

# View logs
sudo journalctl -u attendance.service -f

# Restart service
sudo systemctl restart attendance.service

# Enable service
sudo systemctl enable attendance.service
```

---

## 📊 Result Verification

### Check if system is working
```bash
# 1. Monitor console output
python3 test.py

# 2. Watch CSV file
tail -f attendance.csv

# 3. Check hardware responses
# Green LED should light for known faces
# Red LED should light for unknown faces
# Buzzer should beep accordingly

# 4. Verify Telegram notifications
# Should receive messages for each detection
```

---

## 🆘 Getting Help

### Debugging Steps
1. Enable verbose logging (add print statements)
2. Test individual components with `test_hardware.py`
3. Check error messages in console
4. Review logs: `sudo journalctl -u attendance.service`
5. Search documentation for similar issues

### Information to Include
- Error message (exact text)
- System configuration (RPi model, camera type, etc.)
- Wiring diagram (photo if possible)
- Recent changes made
- Steps to reproduce issue

---

## 📝 Emergency Recovery

### Full system reset
```bash
# Backup current data first!
cp attendance.csv ~/attendance_backup.csv

# Reset everything
cd /home/pi/rfid_attendance
rm attendance.csv unknown_faces/*.jpg

# Recreate CSV
python3 << 'EOF'
import csv
with open('attendance.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['Date', 'Name', 'Roll Number', 'Time', 'Status'])
EOF

# Restart system
python3 test.py
```

---

**Last Updated**: March 13, 2026 | **Support Status**: ✅ Active
