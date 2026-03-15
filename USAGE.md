# Usage Guide

Complete guide on how to operate and use the RFID & Face Recognition Attendance System.

---

## 🎯 Quick Start

### Launch System
```bash
cd /home/pi/rfid_attendance
source venv/bin/activate
python3 test.py
```

### Stop System
Press `q` in the camera window or use `Ctrl+C` in terminal.

---

## 🎬 Running Modes

### Mode 1: Combined System (Recommended)
**Runs face recognition + RFID simultaneously**

```bash
python3 test.py
```

**Features:**
- Real-time camera feed
- Parallel RFID scanning
- Single attendance log for both
- Telegram notifications for both

**Output:**
```
🎥 Camera started. Press 'q' to quit.
🔘 RFID Reader thread started

[System running - waiting for faces/cards]
```

---

### Mode 2: RFID Only
**Only RFID card scanning, no camera**

```bash
python3 rfid.py
```

**Features:**
- Simple RFID detection
- No camera resources needed
- Standalone operation
- Excel file output

**Use Case:** 
- When camera is unavailable
- Standalone kiosk setup
- Lower resource usage

---

### Mode 3: Face Recognition Only
**Disable RFID in test.py**

Edit `test.py` line 14:
```python
# Comment out RFID import
# RFID_AVAILABLE = False
```

---

## 👤 Face Recognition Usage

### Adding New Faces
1. **Create directory** for the person:
   ```bash
   mkdir -p known_faces/new_name
   ```

2. **Add training images** (3-5 images):
   ```bash
   cp ~/path/to/image1.jpg known_faces/new_name/
   cp ~/path/to/image2.jpg known_faces/new_name/
   # ... repeat for more images
   ```

3. **Update student database** in `test.py`:
   ```python
   students = {
       "srinivas": {"roll": "21CS001"},
       "manish": {"roll": "21CS002"},
       "new_name": {"roll": "21CS003"}  # ADD THIS
   }
   ```

4. **Restart system** - New faces load automatically

### Improving Recognition Accuracy

**Better Training Images:**
- ✅ Clear, well-lit photos
- ✅ Multiple angles (front, left, right)
- ✅ Different lighting conditions
- ✅ Neutral expressions
- ✅ Different backgrounds
- ❌ Don't use: Blurry, dark, angled, with glasses

**Adjust Matching Threshold:**
Edit `test.py` line 20:
```python
FACE_MATCH_THRESHOLD = 0.4  # Lower = stricter
# 0.3 = Very strict (few false positives)
# 0.4 = Balanced (recommended)
# 0.6 = Lenient (more matches)
```

**Optimize Processing:**
Edit `test.py` lines 19-22:
```python
FRAME_RESIZE_SCALE = 0.5   # Smaller for speed, 0.75 for accuracy
FRAME_SKIP = 2              # Process fewer frames
```

---

## 🃏 RFID Card Usage

### Registering New Cards

1. **Get card ID** - Scan card with system running:
   ```
   ⚠ RFID UNKNOWN: 1234567890
   ```

2. **Add to system** in `test.py`:
   ```python
   rfid_students = {
       769616991850: {"name": "Srinivas", "roll": "21CS001"},
       1234567890: {"name": "New Name", "roll": "21CS002"}  # ADD THIS
   }
   ```

3. **Restart system** - Card now recognized

### Multiple Cards per Person

Register different card IDs for same person:
```python
rfid_students = {
    769616991850: {"name": "Srinivas", "roll": "21CS001"},
    999888777666: {"name": "Srinivas", "roll": "21CS001"},  # Same person, different card
}
```

---

## 📊 Monitoring & Tracking

### View Attendance Records

**Real-time CSV file:**
```bash
tail -f attendance.csv

# Output:
# 2026-03-13,srinivas,21CS001,08:45:30,Present
# 2026-03-13,manish,21CS002,09:15:45,Absent
```

**Count today's attendance:**
```bash
date=$(date +%Y-%m-%d)
grep "$date" attendance.csv | wc -l
```

**Export to Excel:**
```bash
# Use any spreadsheet application
# File > Open > attendance.csv
```

### Monitor Unknown Faces

**Check unknown face directory:**
```bash
ls -lah unknown_faces/
# Shows: unknown_YYYYMMDD_HHMMSS_N.jpg
```

**View recent unknown faces:**
```bash
find unknown_faces/ -type f -mtime -1 -name "*.jpg" | xargs ls -lt | head -10
```

**Save/Archive unknown faces:**
```bash
tar -czf unknown_faces_$(date +%Y%m%d).tar.gz unknown_faces/
```

---

## 📱 Telegram Notifications

### Setup (One-time)

1. **Create Telegram Bot:**
   - Message [@BotFather](https://t.me/botfather)
   - Send `/newbot`
   - Follow instructions
   - Copy the bot token

2. **Get Chat ID:**
   - Message [@userinfobot](https://t.me/userinfobot)
   - It replies with your chat ID

3. **Add credentials** to `test.py`:
   ```python
   TELEGRAM_BOT_TOKEN = "123456789:ABCDEfghijklmnopqrstuvwxyz"
   TELEGRAM_CHAT_ID = "1234567890"
   ```

4. **Test:**
   ```bash
   python3 test.py
   # Should see notifications when faces/cards detected
   ```

### Notification Types

**Known Face:**
```
✓ Attendance Marked
Name: srinivas
Roll: 21CS001
Status: Present
Time: 08:45:30
```

**Unknown Face (with image):**
```
⚠ Unknown Face Detected
Status: Absent
Time: 09:15:45
Image saved to: unknown_faces/unknown_20260313_091545_0.jpg
```

**Known RFID:**
```
✓ RFID Attendance
Name: Srinivas
Roll: 21CS001
Status: Present
```

**Unknown RFID:**
```
⚠ Unknown RFID Card Detected
ID: 1234567890
```

---

## 🔧 Display & Hardware

### LCD Display Output

**Known Face:**
```
[LCD Line 1: Srinivas    ]
[LCD Line 2: 21CS001 Present]
```

**Unknown Face:**
```
[LCD Line 1: UNKNOWN FACE    ]
[LCD Line 2: 08:45:30        ]
```

**Known RFID:**
```
[LCD Line 1: RFID: Srinivas  ]
[LCD Line 2: 21CS001         ]
```

### LED & Buzzer Feedback

| Event | Green LED | Red LED | Buzzer |
|-------|-----------|---------|--------|
| Known Face | 1s ON | - | 1 beep |
| Unknown Face | - | 1s ON | 5 beeps |
| Known RFID | 1s ON | - | 1 beep |
| Unknown RFID | - | 1s ON | 5 beeps |

---

## ⏱️ Time Settings

### Change Attendance Cutoff Time

Edit `test.py` function `get_attendance_status_time()`:
```python
def get_attendance_status_time():
    current_time_obj = datetime.now().time()
    cutoff_time = datetime.strptime("09:00", "%H:%M").time()  # CHANGE THIS
    
    if current_time_obj <= cutoff_time:
        return "Present"
    else:
        return "Absent"
```

**Examples:**
- `"08:30"` → Present if before 8:30 AM
- `"10:00"` → Present if before 10:00 AM
- `"09:15"` → Present if before 9:15 AM

### Duplicate Prevention

System prevents marking same person twice per minute. Edit [test.py](test.py) line 200 if needed:
```python
minute_key = datetime.now().strftime("%H:%M")  # Current time minute
```

Change to hourly:
```python
minute_key = datetime.now().strftime("%H")  # Hour only
```

---

## 🔐 Data Management

### Backup Attendance Regularly

**Daily backup:**
```bash
cp attendance.csv attendance_$(date +%Y%m%d).csv
```

**Automated daily backup (cron):**
```bash
# Edit crontab
crontab -e

# Add this line:
0 2 * * * cp /home/pi/rfid_attendance/attendance.csv /home/pi/rfid_attendance/backups/attendance_$(date +\%Y\%m\%d).csv
```

### Export to External Storage

```bash
# USB drive
cp attendance.csv /media/pi/USB_DRIVE/
tar -czf attendance_data.tar.gz known_faces/ attendance.csv unknown_faces/

# Cloud (via scp)
scp attendance.csv user@cloud.server:/backups/
```

### Clean Old Unknown Faces

```bash
# Delete faces older than 30 days
find unknown_faces/ -type f -mtime +30 -delete

# Archive old faces instead
find unknown_faces/ -type f -mtime +30 | xargs tar -czf old_faces_$(date +%Y%m%d).tar.gz
```

---

## 🧪 Testing & Debugging

### Test Hardware Components

```bash
source venv/bin/activate
python3 test_hardware.py
```

This tests:
- Green LED
- Red LED
- Buzzer
- LCD display

### Debug Face Detection

```bash
# Add debug output
python3 << 'EOF'
import cv2
import face_recognition
import os

# List all known faces
for person in os.listdir('known_faces'):
    count = len(os.listdir(f'known_faces/{person}'))
    print(f"{person}: {count} images")

# Test face detection
image = face_recognition.load_image_file('known_faces/srinivas/srinivas.jpg')
encodings = face_recognition.face_encodings(image)
print(f"Detected {len(encodings)} face(s)")
EOF
```

### Monitor Camera Performance

```bash
# Check FPS and processing time
python3 << 'EOF'
import cv2
import time

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

start = time.time()
frames = 0

while frames < 30:
    ret, frame = cap.read()
    if ret:
        frames += 1

elapsed = time.time() - start
fps = frames / elapsed
print(f"FPS: {fps:.1f}")
cap.release()
EOF
```

---

## 🚨 Emergency Operations

### Stop Running System

```bash
# Press 'q' in camera window
# OR
sudo systemctl stop attendance.service
# OR
pkill -f "python3 test.py"
```

### Emergency Reset

```bash
# Clear GPIO pins
python3 << 'EOF'
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
GPIO.cleanup()
print("✓ GPIO reset")
EOF

# Clear I2C
sudo i2cset -y 1 0x27 0
```

### Restart Service

```bash
sudo systemctl restart attendance.service
sudo systemctl status attendance.service
```

---

## 📈 Performance Monitoring

### Check System Load

```bash
# CPU and memory usage
top

# Pi CPU temperature
vcgencmd measure_temp

# Storage usage
df -h
```

### Log Analysis

```bash
# If running as service
sudo journalctl -u attendance.service -n 50  # Last 50 lines
sudo journalctl -u attendance.service -f     # Follow live

# Real-time output (if running in terminal)
python3 test.py 2>&1 | tee attendance.log
```

---

## 🎓 Training Staff

### For Administrators

1. **Adding new attendees:**
   - Take 5 clear photos of person
   - Save to `known_faces/{name}/`
   - Add to `students` dict in code
   - Restart system

2. **Troubleshooting:**
   - Check face recognition accuracy
   - Update training images if poor
   - Verify RFID card registration

### For End Users

1. **Physical interaction:**
   - Present face to camera (5-30cm away)
   - Place RFID card near reader
   - Wait for beep (known) or LED response

2. **Expected behavior:**
   - Green LED = Registered (Good!)
   - Red LED = Unknown (Check card/face)
   - Listen for beep pattern

---

## 📞 Troubleshooting

### Face Not Recognized
1. Ensure good lighting
2. Face must be clear and frontal
3. Add more training images
4. Reduce `FACE_MATCH_THRESHOLD`

### RFID Card Not Working
1. Verify card is registered
2. Check RC522 wiring
3. Test with standalone `rfid.py`

### LCD Not Updating
1. Check I2C address (`i2cdetect -y 1`)
2. Update address in `hardware.py` if needed
3. Test with `test_hardware.py`

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for more issues.

---

## 🔄 Regular Maintenance

### Weekly
- [ ] Review attendance records
- [ ] Archive unknown faces
- [ ] Check system logs

### Monthly
- [ ] Backup all data
- [ ] Clean unknown_faces directory
- [ ] Update training images if needed
- [ ] Test all hardware components

### Quarterly
- [ ] Full system audit
- [ ] Camera lens cleaning
- [ ] Update dependencies
- [ ] Performance review

---

**Last Updated**: March 13, 2026 | **Status**: ✅ Production Ready
