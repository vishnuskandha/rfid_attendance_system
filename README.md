# RFID & Face Recognition Attendance System

A comprehensive attendance management system combining RFID card scanning and face recognition technology with hardware integration (LEDs, buzzer, LCD display) and Telegram notifications.

**Raspberry Pi 4/5 | Python 3.11+ | Real-time Processing | Cloud Integration**

---

## 🚀 Features

### Core Functionality
- ✅ **Face Recognition** - Real-time face detection and identification
- ✅ **RFID Integration** - Support for RFID card scanning
- ✅ **Parallel Processing** - Both systems work simultaneously
- ✅ **Dual Attendance** - Same person can be marked via face or RFID
- ✅ **Time-Based Status** - Present (≤09:00) / Absent (>09:00)

### Hardware Integration
- 🟢 **Green LED** - Indicates registered/present
- 🔴 **Red LED** - Indicates unknown/unregistered
- 🔔 **Buzzer** - Audio feedback (1 beep for registered, 5 for unknown)
- 📱 **16x2 LCD Display** - I2C connected for status display
- 📷 **HD Camera** - Real-time video processing

### Data Management
- 📊 **CSV Logging** - All attendance records saved
- 🖼️ **Unknown Face Storage** - Images saved to `unknown_faces/`
- 📲 **Telegram Alerts** - Real-time notifications with images
- 📊 **Attendance Reports** - Exportable data in CSV format

### Performance
- ⚡ **3-4x Faster** - Frame skipping and resizing optimization
- 🎯 **Smart Duplication** - Prevents duplicate marking per minute
- 🔄 **Non-blocking** - Telegram sends in background threads
- 🧵 **Multi-threaded** - RFID and face recognition run in parallel

---

## 📦 System Architecture

```
rfid_attendance/
├── test.py                 # Main system (Face + RFID)
├── rfid.py                 # Standalone RFID system
├── hardware.py             # LED/Buzzer/LCD control
├── known_faces/            # Training data for face recognition
│   ├── srinivas/
│   ├── manish/
│   └── ...
├── unknown_faces/          # Unknown face images
├── attendance.csv          # Attendance records
├── venv/                   # Python virtual environment
└── docs/
    ├── README.md           # This file
    ├── SETUP.md            # Installation guide
    ├── USAGE.md            # Usage instructions
    ├── HARDWARE_SETUP.md   # Hardware configuration
    ├── API_REFERENCE.md    # Function documentation
    └── TROUBLESHOOTING.md  # Common issues
```

---

## ⚡ Quick Start

### 1. Installation (5 minutes)

```bash
# Clone/navigate to project
cd /home/pi/rfid_attendance

# Activate virtual environment
source venv/bin/activate

# Install dependencies (if needed)
pip install face-recognition opencv-python requests smbus2

# Test hardware components
python3 test_hardware.py
```

### 2. Configure System

**Edit student details** - Add names and roll numbers to [test.py](test.py#L43-L46):
```python
students = {
    "name1": {"roll": "21CS001"},
    "name2": {"roll": "21CS002"}
}
```

**Add RFID cards** - Register cards in [test.py](test.py#L48-L52):
```python
rfid_students = {
    769616991850: {"name": "Name", "roll": "21CS001"},
    886622847095: {"name": "Name", "roll": "21CS002"}
}
```

**Set Telegram credentials** - Update in [test.py](test.py#L63-L64):
```python
TELEGRAM_BOT_TOKEN = "your_bot_token"
TELEGRAM_CHAT_ID = "your_chat_id"
```

### 3. Add Face Training Data

Place face images in `known_faces/` directory:
```bash
known_faces/
├── srinivas/
│   ├── srinivas.jpg
│   ├── srinivas_1.jpg
│   └── ...
├── manish/
│   ├── manish.jpg
│   └── ...
```

⚠️ **Requirements:**
- Clear face images
- Good lighting
- Multiple angles (3-5 images per person)
- Face should occupy 50%+ of image
- JPEG or PNG format

### 4. Run System

**Start the combined system:**
```bash
python3 test.py
```

**Or run RFID only:**
```bash
python3 rfid.py
```

---

## 🎯 Attendance Logic

### Time-Based Status
| Time | Status | Notes |
|------|--------|-------|
| ≤ 09:00 | **Present** | On time |
| > 09:00 | **Absent** | Late |

### Detection Methods

**Face Recognition:**
- Real-time camera feed processing
- Compares detected faces against trained encodings
- Marks attendance automatically

**RFID Card:**
- Continuous card scanning
- Matches card ID against registered database
- Immediate attendance marking

**Combined Usage:**
- Same person can use either method
- Duplicate prevention per minute
- All records saved to CSV

---

## 📋 Output Format

### Console Output
```
✓ KNOWN FACE
  Name: srinivas, Roll: 21CS001
  Status: Present | Time: 08:45:30
✓ CSV: srinivas | 21CS001 | Present | 08:45:30
```

### CSV File (attendance.csv)
```
Date,Name,Roll Number,Time,Status
2026-03-13,srinivas,21CS001,08:45:30,Present
2026-03-13,manish,21CS002,09:15:45,Absent
```

### Telegram Notification
```
✓ Attendance Marked
Name: srinivas
Roll: 21CS001
Status: Present
Time: 08:45:30

[Image attached for unknown faces]
```

---

## 🔧 Hardware Setup

### GPIO Pins (Default)
- **Green LED**: GPIO 2
- **Red LED**: GPIO 3
- **Buzzer**: GPIO 4
- **I2C SDA**: GPIO 2 (Pin 3)
- **I2C SCL**: GPIO 3 (Pin 5)

### Wiring Diagram
See [HARDWARE_SETUP.md](HARDWARE_SETUP.md) for detailed wiring instructions.

### LCD Display
- **Type**: 16x2 I2C LCD
- **Default Address**: 0x27 (or 0x3F)
- **Connection**: I2C (2 wires + power)

---

## 📱 Telegram Integration

### Setup Bot
1. Create bot via [@BotFather](https://t.me/botfather)
2. Get bot token
3. Message your bot to get Chat ID
4. Add credentials to `test.py`

### Notifications Sent
- ✅ Registered face detected
- ❌ Unknown face detected (with image)
- ✅ RFID card recognized
- ❌ Unknown card detected

---

## 📊 Data Files

### Generated on Runtime
- **attendance.csv** - All attendance records
- **unknown_faces/** - Directory with unknown face images
  - Format: `unknown_YYYYMMDD_HHMMSS_N.jpg`

### Backed Up Regularly
```bash
# Backup attendance
cp attendance.csv attendance_backup_$(date +%Y%m%d).csv

# Backup unknown faces
tar -czf unknown_faces_backup_$(date +%Y%m%d).tar.gz unknown_faces/
```

---

## ⚙️ Configuration

### Performance Tuning
Edit these in [test.py](test.py#L19-L22):
```python
FRAME_RESIZE_SCALE = 0.5      # Resize frames (0.5 = 50%)
FACE_MATCH_THRESHOLD = 0.4    # Lower = stricter matching
FRAME_SKIP = 2                 # Process every Nth frame
TELEGRAM_TIMEOUT = 3           # Seconds for API timeout
```

### Time Settings
Edit cutoff time in [hardware.py](hardware.py#L152):
```python
cutoff_time = datetime.strptime("09:00", "%H:%M").time()
```

### I2C Address
If LCD at different address, update [hardware.py](hardware.py#L30):
```python
LCD_I2C_ADDRESS = 0x3F  # Try 0x3F if 0x27 doesn't work
```

---

## 🐛 Troubleshooting

### Camera Issues
```bash
# Test camera
libcamera-hello -t 5000

# Check camera connection
vcgencmd get_camera
```

### RFID Not Detected
```bash
# Install RFID library
pip install mfrc522

# Check GPIO permissions
sudo raspi-config
# Interfacing Options > GPIO > Enable
```

### LCD Display Not Working
```bash
# Scan I2C devices
i2cdetect -y 1

# Check address in hardware.py and update if needed
```

### Face Recognition Accuracy
- Add more training images (5+ per person)
- Improve lighting conditions
- Adjust `FACE_MATCH_THRESHOLD` in test.py
- Use different angles for training

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for more solutions.

---

## 📚 Documentation

- [SETUP.md](SETUP.md) - Detailed installation & configuration
- [USAGE.md](USAGE.md) - How to use the system
- [HARDWARE_SETUP.md](HARDWARE_SETUP.md) - Hardware configuration
- [API_REFERENCE.md](API_REFERENCE.md) - Function documentation
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Common issues & fixes

---

## 📝 File Guide

| File | Purpose |
|------|---------|
| `test.py` | Main system with face + RFID |
| `rfid.py` | Standalone RFID system |
| `hardware.py` | LED/Buzzer/LCD control |
| `test_hardware.py` | Hardware testing utility |
| `attendance.csv` | Attendance records |
| `known_faces/` | Face training data |
| `unknown_faces/` | Unknown face images |
| `venv/` | Python dependencies |

---

## 🔐 Security Notes

- ⚠️ **Telegram Token**: Store securely, don't commit to version control
- ⚠️ **GPIO Access**: May require sudo permissions
- ⚠️ **Face Data**: Store training images securely
- ⚠️ **CSV Records**: Contains sensitive attendance data

---

## 📈 Performance Stats

| Metric | Value |
|--------|-------|
| Face Detection | ~2-3 FPS (optimized) |
| RFID Read Time | <1 second |
| Telegram Send | 1-2 seconds (async) |
| CPU Usage | 40-60% during processing |
| Memory | ~200-300 MB |
| Startup Time | 15-20 seconds (dataset loading) |

---

## 🤝 System Integration

### Integration Points
- ✅ CSV export for Excel/Google Sheets
- ✅ Telegram API for notifications
- ✅ GPIO for hardware control
- ✅ I2C for LCD display
- ✅ OpenCV for video processing
- ✅ face_recognition for face encoding

### External APIs
- Telegram Bot API
- Google Sheets (via CSV export)
- Email (via smtp, if configured)

---

## 📞 Support & Issues

### Common Issues
1. **Camera not detected** → Check `vcgencmd get_camera`
2. **RFID not working** → Check GPIO pins and library
3. **LCD blank** → Verify I2C address with `i2cdetect -y 1`
4. **Face accuracy low** → Add more training images

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for detailed solutions.

---

## 📋 License & Credits

- **Framework**: Python 3.11+
- **Face Recognition**: face_recognition library
- **Computer Vision**: OpenCV
- **Hardware**: RPi.GPIO, smbus2
- **API**: Telegram Bot API

---

## 🔄 Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | Mar 13, 2026 | Initial release with RFID + Face Recognition |
| - | - | Hardware integration (LED/Buzzer/LCD) |
| - | - | Telegram notifications |
| - | - | CSV attendance logging |

---

## 📝 Next Steps

1. [SETUP.md](SETUP.md) - Install and configure
2. [USAGE.md](USAGE.md) - Learn how to use
3. [HARDWARE_SETUP.md](HARDWARE_SETUP.md) - Connect hardware
4. Run `python3 test_hardware.py` - Test components
5. Run `python3 test.py` - Start system

---

**Last Updated**: March 13, 2026 | **Maintained By**: Development Team | **Status**: ✅ Production Ready
