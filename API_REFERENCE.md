# API Reference

Complete documentation of all functions and modules in the RFID & Face Recognition Attendance System.

---

## 📦 Modules

### test.py
Main attendance system combining face recognition and RFID.

### rfid.py
Standalone RFID card reader and attendance logger.

### hardware.py
Hardware control module for LEDs, buzzer, and LCD display.

---

## 🎯 test.py Functions

### `get_attendance_status()`
**Purpose:** Determine if late arrival based on current time

**Syntax:**
```python
status = get_attendance_status()
```

**Returns:**
- `"Present"` - If current time <= 09:00
- `"Absent"` - If current time > 09:00

**Example:**
```python
from test import get_attendance_status
status = get_attendance_status()
print(status)  # Output: "Present" or "Absent"
```

---

### `get_student_roll(name)`
**Purpose:** Get student roll number from name

**Syntax:**
```python
roll = get_student_roll(name)
```

**Parameters:**
- `name` (str): Student name (must be in `students` dict)

**Returns:**
- `str`: Roll number
- `"N/A"`: If name not found

**Example:**
```python
roll = get_student_roll("srinivas")
print(roll)  # Output: "21CS001"
```

---

### `save_unknown_face(frame, face_num)`
**Purpose:** Save unknown face image to disk

**Syntax:**
```python
filepath = save_unknown_face(frame, face_num)
```

**Parameters:**
- `frame` (numpy array): Video frame from OpenCV
- `face_num` (int): Face index in frame

**Returns:**
- `str`: Path to saved image

**Example:**
```python
if name == "Unknown":
    path = save_unknown_face(frame, 0)
    print(f"Saved to: {path}")
```

---

### `record_attendance(name, roll, status, timestamp)`
**Purpose:** Save attendance record to CSV file

**Syntax:**
```python
record_attendance(name, roll, status, timestamp)
```

**Parameters:**
- `name` (str): Person's name
- `roll` (str): Roll/ID number
- `status` (str): "Present" or "Absent"
- `timestamp` (str): Format "YYYY-MM-DD HH:MM:SS"

**Returns:**
- None (prints output to console)

**Example:**
```python
from datetime import datetime
timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
record_attendance("srinivas", "21CS001", "Present", timestamp)
```

---

### `send_to_telegram_async(message, image_path=None)`
**Purpose:** Send message to Telegram bot (non-blocking)

**Syntax:**
```python
send_to_telegram_async(message, image_path=None)
```

**Parameters:**
- `message` (str): Text message to send
- `image_path` (str, optional): Path to image file

**Returns:**
- None (runs in background thread)

**Example:**
```python
msg = "Attendance marked for srinivas"
send_to_telegram_async(msg)

# With image
msg = "Unknown face detected"
send_to_telegram_async(msg, "unknown_faces/unknown_001.jpg")
```

---

### `record_rfid_attendance(name, roll)`
**Purpose:** Record RFID attendance to CSV

**Syntax:**
```python
status = record_rfid_attendance(name, roll)
```

**Parameters:**
- `name` (str): Person's name
- `roll` (str): Roll/ID number

**Returns:**
- `str`: Status ("Present" or "Absent")
- `None`: If error

**Example:**
```python
status = record_rfid_attendance("Srinivas", "21CS001")
if status:
    print(f"Status: {status}")
```

---

### `rfid_thread_function(stop_event)`
**Purpose:** Main RFID reader loop (runs in separate thread)

**Syntax:**
```python
rfid_thread = threading.Thread(
    target=rfid_thread_function, 
    args=(stop_event,)
)
rfid_thread.start()
```

**Parameters:**
- `stop_event` (threading.Event): Event to signal thread to stop

**Returns:**
- None (runs indefinitely until stop_event is set)

**Notes:**
- Runs in background
- Continuously scans for RFID cards
- Automatically handles known/unknown cards

---

## 🛠️ hardware.py Functions

### `beep(times=1, duration=0.2, interval=0.2)`
**Purpose:** Control buzzer

**Syntax:**
```python
beep(times=1, duration=0.2, interval=0.2)
```

**Parameters:**
- `times` (int): Number of beeps (default: 1)
- `duration` (float): Seconds per beep (default: 0.2)
- `interval` (float): Seconds between beeps (default: 0.2)

**Returns:**
- None

**Example:**
```python
hardware.beep(1)              # Single beep
hardware.beep(5, 0.15, 0.15)  # 5 quick beeps
```

---

### `set_green_led(state=True, duration=1)`
**Purpose:** Control green LED

**Syntax:**
```python
set_green_led(state=True, duration=1)
```

**Parameters:**
- `state` (bool): True=ON, False=OFF
- `duration` (float): Seconds to stay ON (0 = indefinite)

**Returns:**
- None

**Example:**
```python
hardware.set_green_led(True, 1)   # ON for 1 second
hardware.set_green_led(False)      # Turn OFF
```

---

### `set_red_led(state=True, duration=1)`
**Purpose:** Control red LED

**Syntax:**
```python
set_red_led(state=True, duration=1)
```

**Parameters:**
- `state` (bool): True=ON, False=OFF
- `duration` (float): Seconds to stay ON (0 = indefinite)

**Returns:**
- None

**Example:**
```python
hardware.set_red_led(True, 1)   # ON for 1 second
hardware.set_red_led(False)      # Turn OFF
```

---

### `turn_off_all()`
**Purpose:** Turn off all LEDs and buzzer

**Syntax:**
```python
turn_off_all()
```

**Parameters:**
- None

**Returns:**
- None

**Example:**
```python
hardware.turn_off_all()  # Emergency stop
```

---

### `lcd_write(line1="", line2="")`
**Purpose:** Write text to LCD display

**Syntax:**
```python
lcd_write(line1="", line2="")
```

**Parameters:**
- `line1` (str): Text for first line (max 16 chars)
- `line2` (str): Text for second line (max 16 chars)

**Returns:**
- None

**Example:**
```python
hardware.lcd_write("Name: Srinivas", "Roll: 21CS001")
```

---

### `lcd_known_face(name, roll, status)`
**Purpose:** Display known face info on LCD

**Syntax:**
```python
lcd_known_face(name, roll, status)
```

**Parameters:**
- `name` (str): Person's name
- `roll` (str): Roll number
- `status` (str): "Present" or "Absent"

**Returns:**
- None

**Example:**
```python
hardware.lcd_known_face("Srinivas", "21CS001", "Present")
# Displays:
# "  Srinivas      "
# "21CS001 Present "
```

---

### `lcd_unknown_face()`
**Purpose:** Display unknown face message on LCD

**Syntax:**
```python
lcd_unknown_face()
```

**Parameters:**
- None

**Returns:**
- None

**Example:**
```python
hardware.lcd_unknown_face()
# Displays:
# "UNKNOWN FACE    "
# "08:45:30        "
```

---

### `lcd_registered_rfid(name, roll)`
**Purpose:** Display RFID card info on LCD

**Syntax:**
```python
lcd_registered_rfid(name, roll)
```

**Parameters:**
- `name` (str): Person's name
- `roll` (str): Roll number

**Returns:**
- None

**Example:**
```python
hardware.lcd_registered_rfid("Srinivas", "21CS001")
# Displays:
# "RFID: Srinivas  "
# "21CS001         "
```

---

### `handle_registered(name, roll, status=None)`
**Purpose:** Full response for registered person/card

**Syntax:**
```python
handle_registered(name, roll, status=None)
```

**Parameters:**
- `name` (str): Person's name
- `roll` (str): Roll number
- `status` (str, optional): "Present" or "Absent"

**Returns:**
- None

**Actions:**
- Green LED ON for 1 second
- 1 beep sound
- LCD displays info

**Example:**
```python
hardware.handle_registered("Srinivas", "21CS001", "Present")
```

---

### `handle_unknown()`
**Purpose:** Full response for unknown person/card

**Syntax:**
```python
handle_unknown()
```

**Parameters:**
- None

**Returns:**
- None

**Actions:**
- Red LED ON for 1 second
- 5 beeps sound
- LCD displays "UNKNOWN"

**Example:**
```python
hardware.handle_unknown()
```

---

### `cleanup()`
**Purpose:** Clean up GPIO and resources

**Syntax:**
```python
cleanup()
```

**Parameters:**
- None

**Returns:**
- None

**Example:**
```python
# On system exit
hardware.cleanup()
```

---

## 🎛️ rfid.py Functions

### `beep(times)`
**Purpose:** Control buzzer (local function)

**Syntax:**
```python
beep(times)
```

**Parameters:**
- `times` (int): Number of beeps

**Returns:**
- None

---

## 📊 Data Structures

### Students Dictionary
**Location:** test.py line 43

**Format:**
```python
students = {
    "name1": {"roll": "21CS001"},
    "name2": {"roll": "21CS002"}
}
```

---

### RFID Students Dictionary
**Location:** test.py line 48

**Format:**
```python
rfid_students = {
    769616991850: {"name": "Name1", "roll": "21CS001"},
    886622847095: {"name": "Name2", "roll": "21CS002"}
}
```

---

### CSV Format
**File:** attendance.csv

**Format:**
```
Date,Name,Roll Number,Time,Status
2026-03-13,srinivas,21CS001,08:45:30,Present
2026-03-13,manish,21CS002,09:15:45,Absent
```

---

## 🔧 Configuration Constants

### Frame Processing
```python
FRAME_RESIZE_SCALE = 0.5      # 0.5 = 50% size
FACE_MATCH_THRESHOLD = 0.4    # 0.3-0.6 range
FRAME_SKIP = 2                 # Process every Nth frame
TELEGRAM_TIMEOUT = 3           # Seconds
```

### Hardware Pins
```python
GREEN_LED = 2                  # GPIO 2
RED_LED = 3                    # GPIO 3
BUZZER = 4                     # GPIO 4
```

### I2C Configuration
```python
LCD_I2C_ADDRESS = 0x27         # 0x27 or 0x3F
LCD_I2C_BUS = 1                # RPi I2C bus 1
LCD_COLS = 16                  # 16 character width
LCD_ROWS = 2                   # 2 lines
```

---

## 🔌 GPIO Mapping

| Function | GPIO | Pin |
|----------|------|-----|
| Green LED | 2 | 3 |
| Red LED | 3 | 5 |
| Buzzer | 4 | 7 |
| I2C SDA | 2 | 3 |
| I2C SCL | 3 | 5 |

---

## 🌐 External APIs

### Telegram Bot API
**Endpoint:** `https://api.telegram.org/bot{TOKEN}/`

**Used Methods:**
- `sendMessage` - Send text notification
- `sendPhoto` - Send image with message

**Implementation:** `send_to_telegram_async()`

---

## 📝 Logging & Output

### Console Output Format
```
✓ KNOWN FACE
  Name: srinivas, Roll: 21CS001
  Status: Present | Time: 08:45:30

✓ CSV: srinivas | 21CS001 | Present | 08:45:30
```

### Error Format
```
⚠ CSV Error: [error message]
⚠ Telegram: [error message]
⚠ LCD write error: [error message]
```

---

## 🔐 Security Considerations

### Credentials Storage
- Store Telegram token in environment variables (not in code)
- Use secure methods for credential management
- Never commit secrets to version control

### Data Protection
- CSV contains sensitive attendance data
- Unknown face images may contain identifying info
- Consider encryption for data at rest

---

## 📈 Performance Metrics

| Metric | Value |
|--------|-------|
| Face detection FPS | 2-3 (optimized) |
| RFID read time | <1 second |
| Telegram send | 1-2 seconds |
| CPU usage | 40-60% |
| Memory | 200-300 MB |
| Startup time | 15-20 seconds |

---

## 🤖 Threading Model

### Main Thread
- Camera video capture and processing
- Face recognition and detection
- Drawing and display

### RFID Thread
- Continuous RFID card scanning
- Card validation and logging

### Telegram Thread
- Asynchronous message sending
- Background image upload

---

## 📞 Common Use Cases

### Single Person Attendance
```python
status = get_attendance_status()
record_attendance("srinivas", "21CS001", status, timestamp)
hardware.handle_registered("srinivas", "21CS001", status)
```

### Unknown Face Alert
```python
save_unknown_face(frame, 0)
send_to_telegram_async("Unknown face detected")
hardware.handle_unknown()
```

### RFID Card Processing
```python
if rfid_id in rfid_students:
    name = rfid_students[rfid_id]["name"]
    status = record_rfid_attendance(name, roll)
    hardware.handle_registered(name, roll)
```

---

## 🔍 Debugging Tips

### Enable Verbose Logging
Add print statements:
```python
print(f"DEBUG: Face distance = {best_distance}")
print(f"DEBUG: Match found = {matches[best_match_idx]}")
```

### Check Variable Values
```python
print(f"Students: {students}")
print(f"RFID Students: {rfid_students}")
```

### Test Individual Functions
```python
python3 << 'EOF'
import hardware
hardware.beep(1)
hardware.set_green_led(True, 1)
hardware.lcd_write("Test", "Line")
EOF
```

---

**Last Updated**: March 13, 2026 | **API Version**: 1.0
