import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522
from datetime import datetime
import pandas as pd
import os
import time

# Import hardware module
try:
    import hardware
    HARDWARE_AVAILABLE = True
except ImportError:
    print("⚠ Hardware module not found. Running without LED/Buzzer/LCD")
    hardware = None
    HARDWARE_AVAILABLE = False

# --------------------- Setup ---------------------
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)  # Use BCM numbering

# GPIO pins
GREEN_LED = 2
RED_LED = 3
BUZZER = 4

GPIO.setup(GREEN_LED, GPIO.OUT)
GPIO.setup(RED_LED, GPIO.OUT)
GPIO.setup(BUZZER, GPIO.OUT)

# RFID reader
reader = SimpleMFRC522()

# Registered students
students = {
    769616991850: {"name": "Aru1", "roll": "21CS001"},
    886622847095: {"name": "Vijay", "roll": "21CS002"},
    260401791926: {"name": "Mukesh", "roll": "21CS003"}
}

# Excel file
file_name = "attendance.xlsx"

# --------------------- Create Excel File if Missing ---------------------
if not os.path.exists(file_name):
    df_init = pd.DataFrame(columns=["Date", "Name", "Roll Number", "Time", "Status"])
    df_init.to_excel(file_name, index=False)
    print(f"{file_name} created with correct columns.")

print("RFID Attendance System Ready")
print("Scan your card...")

# --------------------- Buzzer Function ---------------------
def beep(times):
    for _ in range(times):
        GPIO.output(BUZZER, True)
        time.sleep(0.2)
        GPIO.output(BUZZER, False)
        time.sleep(0.2)

# --------------------- Main Loop ---------------------
try:
    while True:
        print("Waiting for card...")
        id, text = reader.read()  # Scan RFID

        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        today_date = now.strftime("%Y-%m-%d")
        current_time_obj = now.time()

        if id in students:
            name = students[id]["name"]
            roll = students[id]["roll"]

            # Attendance rules
            if current_time_obj <= datetime.strptime("09:00", "%H:%M").time():
                status = "Present"
            elif current_time_obj > datetime.strptime("09:10", "%H:%M").time():
                status = "Absent"
            else:
                status = "Late"

            # Read Excel file
            try:
                old_df = pd.read_excel(file_name)
            except Exception:
                old_df = pd.DataFrame(columns=["Date", "Name", "Roll Number", "Time", "Status"])

            # Prevent duplicate attendance for same student on same day
            if not ((old_df["Roll Number"] == roll) & (old_df["Date"] == today_date)).any():
                # Save attendance
                data = {
                    "Date": today_date,
                    "Name": name,
                    "Roll Number": roll,
                    "Time": current_time,
                    "Status": status
                }
                df = pd.DataFrame([data])
                df_to_save = pd.concat([old_df, df], ignore_index=True)
                df_to_save.to_excel(file_name, index=False)

                # HARDWARE: Registered card
                if HARDWARE_AVAILABLE and hardware:
                    hardware.handle_registered(name, roll)
                else:
                    # Fallback: Use GPIO directly
                    GPIO.output(GREEN_LED, True)
                    beep(1)
                    time.sleep(1)
                    GPIO.output(GREEN_LED, False)

                print(f"Attendance marked for {name} ({roll}) at {current_time} - {status}")
                print("----------------------------")
            else:
                print(f"Attendance already marked for {name} today.")
                # HARDWARE: Show on LCD/LED but don't save
                if HARDWARE_AVAILABLE and hardware:
                    hardware.lcd_registered_rfid(name, roll)
                beep(1)

        else:
            # Unknown card
            print("Unknown Card!")
            
            # HARDWARE: Unknown card
            if HARDWARE_AVAILABLE and hardware:
                hardware.handle_unknown()
            else:
                # Fallback: Use GPIO directly
                GPIO.output(RED_LED, True)
                beep(5)
                time.sleep(1)
                GPIO.output(RED_LED, False)

except KeyboardInterrupt:
    print("Exiting...")
    if HARDWARE_AVAILABLE and hardware:
        hardware.cleanup()
    else:
        GPIO.cleanup()
