import cv2
import face_recognition
import numpy as np
import os
from datetime import datetime, date
import csv
import requests
from io import BytesIO
import threading
from collections import defaultdict
import time

# Import RFID module
try:
    from mfrc522 import SimpleMFRC522
    RFID_AVAILABLE = True
except ImportError:
    print("⚠ RFID module not found. Running face recognition only")
    RFID_AVAILABLE = False
    SimpleMFRC522 = None

# Import hardware module
try:
    import hardware
except ImportError:
    print("⚠ Hardware module not found. Running without LED/Buzzer/LCD")
    hardware = None

# -------------------------------
# PERFORMANCE CONFIG
# -------------------------------
FRAME_RESIZE_SCALE = 0.5  # Resize frame to 50% for faster processing
FACE_MATCH_THRESHOLD = 0.4  # Lower = stricter match (0.6 original, 0.4 is better)
FRAME_SKIP = 2  # Process every 2nd frame
TELEGRAM_TIMEOUT = 3  # Seconds for Telegram request

# -------------------------------
# STUDENT DETAILS
# -------------------------------

students = {
    "srinivas": {"roll": "21CS001"},
    "manish": {"roll": "21CS002"}
}

# RFID Registered Cards (RFID ID -> Name, Roll)
rfid_students = {
    769616991850: {"name": "Aru1", "roll": "21CS001"},
    886622847095: {"name": "Vijay", "roll": "21CS002"},
    260401791926: {"name": "Mukesh", "roll": "21CS003"}
}

# CSV file for attendance
attendance_file = "attendance.csv"

# Create CSV if it doesn't exist
if not os.path.exists(attendance_file):
    with open(attendance_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Date", "Name", "Roll Number", "Time", "Status"])

# Telegram config
import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


# Tracking - per day for attendance marking
detected_today = defaultdict(set)  # name -> set of times
detected_unknown_today = set()  # Set of unknown face times

# Frame counter for skipping
frame_count = 0

# -------------------------------
# FUNCTIONS
# -------------------------------

def get_attendance_status():
    """Determine attendance status based on current time"""
    now = datetime.now()
    current_time_obj = now.time()
    cutoff_time = datetime.strptime("09:00", "%H:%M").time()
    
    if current_time_obj <= cutoff_time:
        return "Present"
    else:
        return "Absent"

def get_student_roll(name):
    """Cached student roll lookup"""
    return students.get(name, {}).get("roll", "N/A")

def save_unknown_face(frame, face_num):
    """Save unknown face image"""
    unknown_dir = "unknown_faces"
    os.makedirs(unknown_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(unknown_dir, f"unknown_{timestamp}_{face_num}.jpg")
    
    # Compress image slightly to save space
    cv2.imwrite(filename, frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
    return filename

def record_attendance(name, roll, status, timestamp):
    """Record attendance to CSV"""
    try:
        date_str = timestamp.split(" ")[0]
        time_str = timestamp.split(" ")[1]
        
        with open(attendance_file, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([date_str, name, roll, time_str, status])
        print(f"✓ CSV: {name} | {roll} | {status} | {time_str}")
    except Exception as e:
        print(f"⚠ CSV Error: {e}")

def send_to_telegram_async(message, image_path=None):
    """Send to Telegram asynchronously (non-blocking)"""
    def _send():
        if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
            return
        
        try:
            url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
            payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
            requests.post(url, json=payload, timeout=TELEGRAM_TIMEOUT)
            
            if image_path and os.path.exists(image_path):
                url_photo = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"
                with open(image_path, 'rb') as photo:
                    files = {'photo': photo}
                    requests.post(url_photo, data={"chat_id": TELEGRAM_CHAT_ID}, 
                                files=files, timeout=TELEGRAM_TIMEOUT)
        except Exception as e:
            print(f"⚠ Telegram: {e}")
    
    # Run in background thread
    thread = threading.Thread(target=_send, daemon=True)
    thread.start()

# ==================== RFID FUNCTIONS ====================

def get_attendance_status_time():
    """Get attendance status based on current time"""
    current_time_obj = datetime.now().time()
    cutoff_time = datetime.strptime("09:00", "%H:%M").time()
    
    if current_time_obj <= cutoff_time:
        return "Present"
    else:
        return "Absent"

def record_rfid_attendance(name, roll):
    """Record RFID attendance to CSV"""
    try:
        now = datetime.now()
        date_str = now.strftime("%Y-%m-%d")
        time_str = now.strftime("%H:%M:%S")
        status = get_attendance_status_time()
        
        with open(attendance_file, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([date_str, name, roll, time_str, status])
        
        print(f"\n✓ RFID ATTENDANCE MARKED")
        print(f"  Name: {name}, Roll: {roll}")
        print(f"  Status: {status} | Time: {time_str}")
        
        return status
    except Exception as e:
        print(f"⚠ RFID CSV Error: {e}")
        return None

def rfid_thread_function(stop_event):
    """
    Run RFID reader in a separate thread
    Continuously scans for RFID cards
    """
    if not RFID_AVAILABLE:
        print("⚠ RFID not available")
        return
    
    print("🔘 RFID Reader Starting...")
    
    try:
        reader = SimpleMFRC522()
        rfid_detected = {}  # Track detected cards
        
        while not stop_event.is_set():
            try:
                print("Waiting for RFID card...")
                rfid_id, text = reader.read()
                
                # Prevent duplicate detection (same card multiple times per minute)
                minute_key = datetime.now().strftime("%H:%M")
                card_key = f"{rfid_id}_{minute_key}"
                
                if card_key not in rfid_detected:
                    
                    if rfid_id in rfid_students:
                        # Known card
                        name = rfid_students[rfid_id]["name"]
                        roll = rfid_students[rfid_id]["roll"]
                        
                        print(f"\n✓ RFID REGISTERED: {name}")
                        
                        # Hardware response
                        if hardware:
                            hardware.handle_registered(name, roll)
                        
                        # Record attendance
                        status = record_rfid_attendance(name, roll)
                        
                        # Send to Telegram
                        msg = f"✓ RFID Attendance\nName: {name}\nRoll: {roll}\nStatus: {status}"
                        send_to_telegram_async(msg)
                        
                    else:
                        # Unknown card
                        print(f"\n⚠ RFID UNKNOWN: {rfid_id}")
                        
                        # Hardware response
                        if hardware:
                            hardware.handle_unknown()
                        
                        # Send to Telegram
                        msg = f"⚠ Unknown RFID Card Detected\nID: {rfid_id}"
                        send_to_telegram_async(msg)
                    
                    rfid_detected[card_key] = True
                
                time.sleep(0.5)  # Small delay to prevent busy waiting
                
            except Exception as e:
                print(f"⚠ RFID Read Error: {e}")
                time.sleep(1)
    
    except Exception as e:
        print(f"⚠ RFID Thread Error: {e}")
    
    finally:
        print("🔘 RFID Reader Stopped")

# ==================== END RFID FUNCTIONS ====================

# -------------------------------
# LOAD DATASET
# -------------------------------

known_face_encodings = []
known_face_names = []

dataset_path = "known_faces"

print("Loading dataset...")

for item in os.listdir(dataset_path):
    item_path = os.path.join(dataset_path, item)
    
    if os.path.isdir(item_path):
        person = item
        for img_name in os.listdir(item_path):
            img_path = os.path.join(item_path, img_name)
            if img_name.lower().endswith(('.jpg', '.jpeg', '.png')):
                image = cv2.imread(img_path)
                if image is not None:
                    rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                    encodings = face_recognition.face_encodings(rgb)
                    if len(encodings) > 0:
                        known_face_encodings.append(encodings[0])
                        known_face_names.append(person)
                        print(f"  ✓ {person} from {img_name}")
    
    elif item.lower().endswith(('.jpg', '.jpeg', '.png')):
        person = os.path.splitext(item)[0]
        image = cv2.imread(item_path)
        if image is not None:
            rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            encodings = face_recognition.face_encodings(rgb)
            if len(encodings) > 0:
                known_face_encodings.append(encodings[0])
                known_face_names.append(person)
                print(f"  ✓ {person} from {item}")

print(f"✓ {len(known_face_encodings)} encodings loaded\n")

# Convert to numpy arrays for faster comparison
known_face_encodings = np.array(known_face_encodings)

# -------------------------------
# RFID THREAD SETUP
# -------------------------------

rfid_stop_event = threading.Event()

if RFID_AVAILABLE:
    rfid_thread = threading.Thread(target=rfid_thread_function, args=(rfid_stop_event,), daemon=True)
    rfid_thread.start()
    print("✓ RFID thread started\n")
else:
    print("⚠ RFID not available - face recognition only\n")

# -------------------------------
# CAMERA START
# -------------------------------

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

print("🎥 Camera started. Press 'q' to quit.\n")

# -------------------------------
# FACE LOOP
# -------------------------------

while True:
    ret, frame = cap.read()
    
    if not ret:
        break
    
    frame_count += 1
    
    # Process only every Nth frame for speed
    if frame_count % FRAME_SKIP != 0:
        cv2.imshow("Attendance System", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
        continue
    
    # Resize for faster processing
    small_frame = cv2.resize(frame, (0, 0), fx=FRAME_RESIZE_SCALE, fy=FRAME_RESIZE_SCALE)
    rgb_small = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
    
    # Detect faces
    face_locations = face_recognition.face_locations(rgb_small, model="hog")  # Faster than CNN
    face_encodings = face_recognition.face_encodings(rgb_small, face_locations)
    
    for face_idx, (face_location, face_encoding) in enumerate(zip(face_locations, face_encodings)):
        
        # Scale back to original frame size
        top, right, bottom, left = face_location
        top, right, bottom, left = int(top / FRAME_RESIZE_SCALE), int(right / FRAME_RESIZE_SCALE), \
                                   int(bottom / FRAME_RESIZE_SCALE), int(left / FRAME_RESIZE_SCALE)
        
        # Compare faces
        face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
        best_match_idx = np.argmin(face_distances)
        best_distance = face_distances[best_match_idx]
        
        name = "Unknown"
        if best_distance < FACE_MATCH_THRESHOLD:
            name = known_face_names[best_match_idx]
        
        # -----------------------
        # KNOWN STUDENT
        # -----------------------
        if name != "Unknown":
            roll = get_student_roll(name)
            time_now = datetime.now().strftime("%H:%M:%S")
            date_now = datetime.now().strftime("%Y-%m-%d")
            timestamp = f"{date_now} {time_now}"
            status = get_attendance_status()
            
            text = f"{name} | {roll} | {status}"
            
            # Mark only once per day (at specific minute to avoid duplicates)
            minute_key = datetime.now().strftime("%H:%M")
            if minute_key not in detected_today[name]:
                
                print("\n✓ KNOWN FACE")
                print(f"  Name: {name}, Roll: {roll}")
                print(f"  Status: {status} | Time: {time_now}")
                
                # HARDWARE: Known face detected
                if hardware:
                    hardware.handle_registered(name, roll, status)
                
                record_attendance(name, roll, status, timestamp)
                msg = f"✓ Attendance\nName: {name}\nRoll: {roll}\nStatus: {status}\nTime: {time_now}"
                send_to_telegram_async(msg)
                
                detected_today[name].add(minute_key)
            
            color = (0, 255, 0)
        
        # -----------------------
        # UNKNOWN FACE
        # -----------------------
        else:
            time_now = datetime.now().strftime("%H:%M:%S")
            date_now = datetime.now().strftime("%Y-%m-%d")
            status = get_attendance_status()
            text = "Unknown"
            
            # Mark once per minute
            minute_key = datetime.now().strftime("%H:%M")
            if minute_key not in detected_unknown_today:
                
                print(f"\n⚠ UNKNOWN FACE | {status} | {time_now}")
                
                # HARDWARE: Unknown face detected
                if hardware:
                    hardware.handle_unknown()
                
                img_path = save_unknown_face(frame, face_idx)
                msg = f"⚠ Unknown Face\nStatus: {status}\nTime: {time_now}"
                send_to_telegram_async(msg, img_path)
                
                detected_unknown_today.add(minute_key)
            
            color = (0, 0, 255)
        
        # Draw on frame
        cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
        cv2.putText(frame, text, (left, top - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
    
    # Show frame
    cv2.imshow("Attendance System", frame)
    
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
print("\n✓ System stopped")

# Stop RFID thread
print("Stopping RFID thread...")
rfid_stop_event.set()
time.sleep(1)

# Cleanup hardware
if hardware:
    hardware.cleanup()
