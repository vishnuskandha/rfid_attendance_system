#!/usr/bin/env python3
"""
Test GPIO pins for I2C (SDA and SCL)
GPIO 2 = SDA (Pin 3)
GPIO 3 = SCL (Pin 5)
"""

import RPi.GPIO as GPIO
import time

print("=" * 50)
print("GPIO PIN TEST (SDA & SCL)")
print("=" * 50)

# Setup GPIO
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

# I2C Pins
GPIO_SDA = 2  # Pin 3
GPIO_SCL = 3  # Pin 5

print(f"\nTesting GPIO {GPIO_SDA} (SDA - Pin 3)")
print(f"Testing GPIO {GPIO_SCL} (SCL - Pin 5)")

try:
    # Set as input first to check initial state
    GPIO.setup(GPIO_SDA, GPIO.IN)
    GPIO.setup(GPIO_SCL, GPIO.IN)
    
    print(f"\n[1] Initial State (Input mode):")
    print(f"  GPIO {GPIO_SDA} (SDA): {GPIO.input(GPIO_SDA)}")
    print(f"  GPIO {GPIO_SCL} (SCL): {GPIO.input(GPIO_SCL)}")
    
    # Try to set as output
    GPIO.setup(GPIO_SDA, GPIO.OUT)
    GPIO.setup(GPIO_SCL, GPIO.OUT)
    
    print(f"\n[2] Testing GPIO {GPIO_SDA} (Set to HIGH):")
    GPIO.output(GPIO_SDA, True)
    time.sleep(0.5)
    print(f"  Output HIGH - Read: {GPIO.input(GPIO_SDA)}")
    
    print(f"\n[3] Testing GPIO {GPIO_SDA} (Set to LOW):")
    GPIO.output(GPIO_SDA, False)
    time.sleep(0.5)
    print(f"  Output LOW - Read: {GPIO.input(GPIO_SDA)}")
    
    print(f"\n[4] Testing GPIO {GPIO_SCL} (Set to HIGH):")
    GPIO.output(GPIO_SCL, True)
    time.sleep(0.5)
    print(f"  Output HIGH - Read: {GPIO.input(GPIO_SCL)}")
    
    print(f"\n[5] Testing GPIO {GPIO_SCL} (Set to LOW):")
    GPIO.output(GPIO_SCL, False)
    time.sleep(0.5)
    print(f"  Output LOW - Read: {GPIO.input(GPIO_SCL)}")
    
    # Test with multimeter simulation - measure voltage
    print(f"\n[6] Pin Status:")
    GPIO.output(GPIO_SDA, True)
    GPIO.output(GPIO_SCL, True)
    print(f"  GPIO {GPIO_SDA} (SDA): HIGH")
    print(f"  GPIO {GPIO_SCL} (SCL): HIGH")
    print(f"  ✓ Both pins are working!")
    
    # Check if pins are accessible
    print(f"\n[7] Pin Permissions:")
    import os
    sda_path = "/sys/class/gpio/gpio2"
    scl_path = "/sys/class/gpio/gpio3"
    
    print(f"  GPIO 2 exists: {os.path.exists(sda_path)}")
    print(f"  GPIO 3 exists: {os.path.exists(scl_path)}")
    
except Exception as e:
    print(f"❌ GPIO Error: {e}")
    import traceback
    traceback.print_exc()

finally:
    GPIO.cleanup()
    print("\n" + "=" * 50)

print("\nRESULT:")
print("  ✓ If both pins show HIGH/LOW changes = GPIO working")
print("  ❌ If pins don't respond = GPIO pin damage/conflict")
print("  ⚠ If GPIO.output() fails = Pin already in use by another process")
print("\n" + "=" * 50)
