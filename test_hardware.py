#!/usr/bin/env python3
"""
Hardware test script - verifies LED, buzzer, and LCD functionality
Run this to test hardware before running the main attendance system
"""

import sys
sys.path.insert(0, '/home/pi/rfid_attendance')

import hardware
import time

print("\n" + "="*50)
print("HARDWARE TEST - Face Recognition System")
print("="*50)

try:
    print("\n[1] Testing Green LED (1 second)...")
    hardware.set_green_led(True, duration=1)
    time.sleep(0.5)
    print("✓ Green LED OK")
    
    print("\n[2] Testing Red LED (1 second)...")
    hardware.set_red_led(True, duration=1)
    time.sleep(0.5)
    print("✓ Red LED OK")
    
    print("\n[3] Testing Buzzer (1 beep)...")
    hardware.beep(1, duration=0.2, interval=0.2)
    time.sleep(0.5)
    print("✓ Buzzer OK")
    
    print("\n[4] Testing LCD (Registered face)...")
    hardware.lcd_known_face("Srinivas", "21CS001", "Present")
    time.sleep(2)
    print("✓ LCD OK (Known face)")
    
    print("\n[5] Testing LCD (Unknown face)...")
    hardware.lcd_unknown_face()
    time.sleep(2)
    print("✓ LCD OK (Unknown face)")
    
    print("\n[6] Testing full registered response...")
    hardware.handle_registered("John Doe", "21CS999", "Absent")
    time.sleep(1.5)
    print("✓ Handle registered OK")
    
    print("\n[7] Testing full unknown response...")
    hardware.handle_unknown()
    time.sleep(1.5)
    print("✓ Handle unknown OK")
    
    print("\n" + "="*50)
    print("✅ ALL HARDWARE TESTS PASSED!")
    print("="*50)
    
except Exception as e:
    print(f"\n❌ TEST FAILED: {e}")
    import traceback
    traceback.print_exc()

finally:
    print("\nCleaning up...")
    hardware.cleanup()
    print("✓ Done")
