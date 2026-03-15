#!/usr/bin/env python3
"""
LCD Display Test Script
Debug I2C connection and LCD functionality
"""

import smbus2
import time

print("=" * 50)
print("LCD I2C DISPLAY TEST")
print("=" * 50)

# I2C Configuration
LCD_I2C_BUS = 1
LCD_I2C_ADDRESS = 0x27

print("\n[1] Checking I2C Bus...")
try:
    bus = smbus2.SMBus(LCD_I2C_BUS)
    print("✓ I2C Bus initialized successfully")
except Exception as e:
    print(f"❌ I2C Bus Error: {e}")
    print("Make sure I2C is enabled on Raspberry Pi")
    exit(1)

print("\n[2] Scanning I2C devices...")
devices_found = []
for addr in range(0x03, 0x78):
    try:
        bus.read_byte(addr)
        devices_found.append(addr)
        print(f"✓ Device found at 0x{addr:02x}")
    except:
        pass

if not devices_found:
    print("❌ No I2C devices found!")
    print("Check your connections:")
    print("  - SDA (GPIO 2) connected to LCD module")
    print("  - SCL (GPIO 3) connected to LCD module")
    print("  - GND and +5V connected")
    exit(1)

print(f"\nTotal devices found: {len(devices_found)}")

print(f"\n[3] Checking LCD at address 0x{LCD_I2C_ADDRESS:02x}...")
if LCD_I2C_ADDRESS in devices_found:
    print(f"✓ LCD detected at address 0x{LCD_I2C_ADDRESS:02x}")
else:
    print(f"❌ LCD not found at 0x{LCD_I2C_ADDRESS:02x}")
    print(f"Available addresses: {[hex(d) for d in devices_found]}")
    print("\nTry changing LCD_I2C_ADDRESS in hardware.py to one of the above")
    exit(1)

print("\n[4] Testing I2C communication...")
try:
    for i in range(5):
        bus.write_byte(LCD_I2C_ADDRESS, 0x08)  # Backlight on
        time.sleep(0.2)
        bus.write_byte(LCD_I2C_ADDRESS, 0x00)  # Backlight off
        time.sleep(0.2)
    print("✓ I2C communication successful")
    bus.write_byte(LCD_I2C_ADDRESS, 0x08)  # Leave backlight on
except Exception as e:
    print(f"❌ I2C Communication Error: {e}")
    exit(1)

print("\n[5] Testing LCD Display...")
try:
    # Import hardware module to test LCD functions
    import sys
    sys.path.insert(0, '/home/pi/rfid_attendance')
    import hardware
    
    print("✓ Hardware module imported")
    
    # Initialize LCD
    if hardware.lcd:
        print("✓ LCD initialized")
        
        # Test display
        hardware.lcd_write("TEST DISPLAY", "LCD WORKING! ✓")
        time.sleep(2)
        
        hardware.lcd_write("Known Face", "Srinivas 21CS001")
        time.sleep(2)
        
        hardware.lcd_write("Unknown Face", "14:30:45")
        time.sleep(2)
        
        hardware.lcd_write("Attendance OK", datetime.now().strftime("%H:%M:%S"))
        time.sleep(2)
        
        print("✓ LCD display test passed!")
    else:
        print("⚠ LCD not initialized in hardware module")
        
except Exception as e:
    print(f"❌ LCD Test Error: {e}")
    import traceback
    traceback.print_exc()

bus.close()

print("\n" + "=" * 50)
print("TEST COMPLETE")
print("=" * 50)
print("\nIf LCD is not showing anything:")
print("1. Check physical connections (SDA, SCL, GND, +5V)")
print("2. Check I2C address: i2cdetect -y 1")
print("3. Try 0x3F instead of 0x27 in hardware.py")
print("4. Check LCD contrast knob (potentiometer)")
print("=" * 50)
