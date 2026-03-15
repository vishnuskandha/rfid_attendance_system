# -*- coding: utf-8 -*-

import cv2
import face_recognition
import os
from datetime import datetime

# ---------------- SAVE UNKNOWN FACE ----------------
def save_unknown_face(frame):
    folder = "unknown_faces"

    if not os.path.exists(folder):
        os.makedirs(folder)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{folder}/unknown_{timestamp}.jpg"

    cv2.imwrite(filename, frame)
    print("Unknown face saved:", filename)


# ---------------- LOAD KNOWN FACES ----------------
known_faces = []
known_names = []

face_files = ["faces/11.jpg", "faces/12.jpg", "faces/13.jpg"]
names = ["Arivu", "Virat", "Modi"]

for file, name in zip(face_files, names):
    img = face_recognition.load_image_file(file)
    encodings = face_recognition.face_encodings(img)

    if encodings:
        known_faces.append(encodings[0])
        known_names.append(name)

print("Known faces loaded")


# ---------------- START CAMERA ----------------
video = cv2.VideoCapture(0)   # USB Camera

print("Face Recognition Started")

while True:

    ret, frame = video.read()
    if not ret:
        break

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    small_frame = cv2.resize(rgb, (0,0), fx=0.25, fy=0.25)

    locations = face_recognition.face_locations(small_frame)
    encodings = face_recognition.face_encodings(small_frame, locations)

    name = "Unknown"

    for face_encoding in encodings:

        matches = face_recognition.compare_faces(known_faces, face_encoding)

        if True in matches:
            index = matches.index(True)
            name = known_names[index]
            print("Authorized Face:", name)
        else:
            print("Unknown Face Detected")
            save_unknown_face(frame)

    # Draw box on face
    for (top, right, bottom, left) in locations:

        top *= 4
        right *= 4
        bottom *= 4
        left *= 4

        cv2.rectangle(frame, (left, top), (right, bottom), (0,255,0), 2)
        cv2.putText(frame, name, (left, top-10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0,255,0), 2)

    cv2.imshow("Face Recognition - USB Camera", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break


video.release()
cv2.destroyAllWindows()