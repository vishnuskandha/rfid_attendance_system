import cv2
import face_recognition
import time
from picamera2 import Picamera2

# ---------------- CAMERA SETUP ----------------
picam2 = Picamera2()
picam2.configure(
    picam2.create_preview_configuration(
        main={"format": "RGB888", "size": (640, 480)}
    )
)
picam2.start()

# ---------------- FACE DOOR AUTH ----------------
def start_face_door_auth():
    known_faces = []
    known_names = []

    face_files = ["faces/11.jpg", "faces/12.jpg", "faces/13.jpg"]
    names = ["Arivu", "Virat", "Modi"]

    # Load known faces
    for file, name in zip(face_files, names):
        img = face_recognition.load_image_file(file)
        encodings = face_recognition.face_encodings(img)
        if encodings:
            known_faces.append(encodings[0])
            known_names.append(name)

    print("🚪 Smart Door Authentication (Pi Camera) Started")

    while True:
        frame = picam2.capture_array()

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        small = cv2.resize(rgb, (0, 0), fx=0.25, fy=0.25)

        locations = face_recognition.face_locations(small)
        encodings = face_recognition.face_encodings(small, locations)

        status = "NO FACE DETECTED"
        color = (0, 255, 255)

        for face in encodings:
            matches = face_recognition.compare_faces(known_faces, face)

            # ✅ Authorized
            if True in matches:
                name = known_names[matches.index(True)]
                status = f"DOOR OPEN – WELCOME {name}"
                color = (0, 255, 0)

                cv2.putText(frame, status, (20, 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 1.1, color, 3)
                cv2.imshow("Smart Door", frame)

                print("✅ Authorized – Door Opened")
                time.sleep(2)
                cv2.destroyAllWindows()
                return True

            # ❌ Unauthorized
            else:
                status = "ACCESS DENIED – DOOR CLOSED"
                color = (0, 0, 255)

                cv2.putText(frame, status, (20, 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 1.1, color, 3)
                cv2.imshow("Smart Door", frame)

                print("❌ Unauthorized – Door Closed")
                time.sleep(2)
                cv2.destroyAllWindows()
                return False

        cv2.putText(frame, status, (20, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.1, color, 3)
        cv2.imshow("Smart Door", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cv2.destroyAllWindows()
    return False


# ---------------- RUN ----------------
if __name__ == "__main__":
    access = start_face_door_auth()

    if access:
        print("🏠 Entry Allowed")
    else:
        print("🚫 Entry Denied")
