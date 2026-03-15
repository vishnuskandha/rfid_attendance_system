# -*- coding: utf-8 -*-

import cv2
import face_recognition
import time
import RPi.GPIO as GPIO
from picamera2 import Picamera2
import os
from datetime import datetime

# ---------------- GPIO SETUP ----------------
GPIO.setwarnings(False)
GPIO.cleanup()
GPIO.setmode(GPIO.BCM)

BUZZER = 18
GPIO.setup(BUZZER, GPIO.OUT)
GPIO.output(BUZZER, GPIO.LOW)

# ---------------- KEYPAD SETUP ----------------
ROWS = [5, 6, 13, 19]        # R1 R2 R3 R4
COLS = [12, 16, 20, 21]     # C1 C2 C3 C4

KEYS = [
    ['1','2','3','A'],
    ['4','5','6','B'],
    ['7','8','9','C'],
    ['*','0','#','D']
]

for r in ROWS:
    GPIO.setup(r, GPIO.OUT)
    GPIO.output(r, GPIO.HIGH)

for c in COLS:
    GPIO.setup(c, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def get_key():
    for i in range(4):
        GPIO.output(ROWS[i], GPIO.LOW)
        for j in range(4):
            if GPIO.input(COLS[j]) == GPIO.LOW:
                time.sleep(0.25)
                while GPIO.input(COLS[j]) == GPIO.LOW:
                    time.sleep(0.05)
                GPIO.output(ROWS[i], GPIO.HIGH)
                return KEYS[i][j]
        GPIO.output(ROWS[i], GPIO.HIGH)
    return None

# ---------------- SAVE UNAUTHORIZED FACE ----------------
def save_unauthorized_face(frame):
    folder = "unauthorized_faces"
    if not os.path.exists(folder):
        os.makedirs(folder)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{folder}/unauth_{timestamp}.jpg"
    cv2.imwrite(filename, frame)
    print(f"Unauthorized face saved: {filename}")

# ---------------- FACE AUTH ----------------
def face_auth():
    picam2 = Picamera2()
    picam2.configure(
        picam2.create_preview_configuration(
            main={"format": "RGB888", "size": (640, 480)}
        )
    )
    picam2.start()

    known_faces = []
    known_names = []

    face_files = ["faces/11.jpg", "faces/12.jpg", "faces/13.jpg"]
    names = ["Arivu", "Virat", "Modi"]

    for f, n in zip(face_files, names):
        img = face_recognition.load_image_file(f)
        enc = face_recognition.face_encodings(img)
        if enc:
            known_faces.append(enc[0])
            known_names.append(n)

    print("Face Authentication Started")

    timeout = time.time() + 10  # 10 seconds

    while time.time() < timeout:
        frame = picam2.capture_array()
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        small = cv2.resize(rgb, (0, 0), fx=0.25, fy=0.25)

        locations = face_recognition.face_locations(small)
        encodings = face_recognition.face_encodings(small, locations)

        for face in encodings:
            matches = face_recognition.compare_faces(known_faces, face)
            if True in matches:
                name = known_names[matches.index(True)]
                print("Authorized Face:", name)

                cv2.destroyAllWindows()
                picam2.stop()
                return True

        cv2.imshow("Smart Door - Face Scan", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Face not recognized
    cv2.destroyAllWindows()
    frame = picam2.capture_array()
    save_unauthorized_face(frame)
    picam2.stop()
    return False

# ---------------- KEYPAD AUTH ----------------
def keypad_auth():
    PASSWORD = "1234"
    entered = ""
    attempts = 0

    print("Keypad Authentication Started")

    while True:
        key = get_key()
        if key:
            if key == '#':
                print()
                if entered == PASSWORD:
                    print("Keypad Access Granted")
                    GPIO.output(BUZZER, GPIO.LOW)
                    return True
                else:
                    print("Wrong Password")
                    attempts += 1
                entered = ""

                if attempts == 3:
                    print("ALERT! 3 Wrong Attempts")
                    GPIO.output(BUZZER, GPIO.HIGH)
                    return False

            elif key == '*':
                entered = ""
                print("\nCleared")
            else:
                entered += key
                print("*", end="", flush=True)

        time.sleep(0.1)

# ---------------- MAIN ----------------
if __name__ == "__main__":
    access = face_auth()

    if access:
        print("Door Opened by Face")
    else:
        print("Face Not Recognized")
        GPIO.output(BUZZER, GPIO.HIGH)
        keypad_auth()
