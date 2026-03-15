"""
Hardware module for GPIO control (LEDs, Buzzer) and LCD display
Supports 16x2 I2C LCD display with PCF8574 I2C expander
"""

import RPi.GPIO as GPIO
import time
from datetime import datetime
import smbus2
import time as time_module

# GPIO Setup
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

# GPIO pins
GREEN_LED = 17
RED_LED = 27
BUZZER = 22

GPIO.setup(GREEN_LED, GPIO.OUT)
GPIO.setup(RED_LED, GPIO.OUT)
GPIO.setup(BUZZER, GPIO.OUT)

# LCD I2C Configuration
LCD_I2C_ADDRESS = 0x27  # Default address (try 0x3F if this doesn't work)
LCD_I2C_BUS = 1
LCD_COLS = 16
LCD_ROWS = 2

# Initialize I2C bus and LCD
bus = None
lcd = None

try:
    bus = smbus2.SMBus(LCD_I2C_BUS)
    print("✓ I2C Bus initialized")
    
    # Try to detect LCD at the address
    try:
        bus.read_byte(LCD_I2C_ADDRESS)
        print(f"✓ LCD detected at address 0x{LCD_I2C_ADDRESS:02x}")
        lcd = True
    except:
        print(f"⚠ LCD not detected at 0x{LCD_I2C_ADDRESS:02x}")
        lcd = None
        
except Exception as e:
    print(f"⚠ I2C initialization failed: {e}")
    bus = None
    lcd = None

# LCD Control Constants
LCD_ENABLE = 0x04
LCD_RW = 0x02
LCD_RS = 0x01
LCD_BACKLIGHT = 0x08

def lcd_write_nibble(byte):
    """Write 4-bit data to LCD"""
    if not bus or not lcd:
        return
    try:
        # Send high nibble with enable pulse
        bus.write_byte(LCD_I2C_ADDRESS, (byte & 0xF0) | LCD_BACKLIGHT)
        bus.write_byte(LCD_I2C_ADDRESS, (byte & 0xF0) | LCD_ENABLE | LCD_BACKLIGHT)
        time_module.sleep(0.001)
        bus.write_byte(LCD_I2C_ADDRESS, (byte & 0xF0) | LCD_BACKLIGHT)
    except:
        pass

def lcd_write_byte(data, mode=0):
    """Write byte to LCD"""
    if not bus or not lcd:
        return
    try:
        high = data & 0xF0
        low = (data << 4) & 0xF0
        
        # Send high nibble
        bus.write_byte(LCD_I2C_ADDRESS, high | mode | LCD_BACKLIGHT)
        bus.write_byte(LCD_I2C_ADDRESS, high | mode | LCD_ENABLE | LCD_BACKLIGHT)
        time_module.sleep(0.001)
        bus.write_byte(LCD_I2C_ADDRESS, high | mode | LCD_BACKLIGHT)
        
        # Send low nibble
        bus.write_byte(LCD_I2C_ADDRESS, low | mode | LCD_BACKLIGHT)
        bus.write_byte(LCD_I2C_ADDRESS, low | mode | LCD_ENABLE | LCD_BACKLIGHT)
        time_module.sleep(0.001)
        bus.write_byte(LCD_I2C_ADDRESS, low | mode | LCD_BACKLIGHT)
    except:
        pass

def lcd_init():
    """Initialize LCD display"""
    if not bus or not lcd:
        return
    try:
        time_module.sleep(0.05)
        lcd_write_nibble(0x30)
        time_module.sleep(0.01)
        lcd_write_nibble(0x30)
        time_module.sleep(0.01)
        lcd_write_nibble(0x30)
        time_module.sleep(0.01)
        lcd_write_nibble(0x20)
        time_module.sleep(0.01)
        
        # Function set: 4-bit mode, 2 lines, 5x8 font
        lcd_write_byte(0x28, 0)
        time_module.sleep(0.01)
        
        # Display on, cursor off, no blink
        lcd_write_byte(0x0C, 0)
        time_module.sleep(0.01)
        
        # Clear display
        lcd_write_byte(0x01, 0)
        time_module.sleep(0.01)
        
        # Entry mode: increment, no shift
        lcd_write_byte(0x06, 0)
        time_module.sleep(0.01)
        
        print("✓ LCD initialized")
        return True
    except Exception as e:
        print(f"⚠ LCD init error: {e}")
        return False

# ==================== LED & BUZZER FUNCTIONS ====================

def beep(times=1, duration=0.2, interval=0.2):
    """
    Beep the buzzer
    Args:
        times: Number of beeps
        duration: Duration of each beep in seconds
        interval: Interval between beeps in seconds
    """
    for _ in range(times):
        GPIO.output(BUZZER, True)
        time.sleep(duration)
        GPIO.output(BUZZER, False)
        time.sleep(interval)

def set_green_led(state=True, duration=1):
    """
    Control green LED (Registered/Present)
    Args:
        state: True=ON, False=OFF
        duration: Time to keep LED on (0 = indefinite)
    """
    GPIO.output(GREEN_LED, state)
    if duration > 0 and state:
        time.sleep(duration)
        GPIO.output(GREEN_LED, False)

def set_red_led(state=True, duration=1):
    """
    Control red LED (Unknown/Absent)
    Args:
        state: True=ON, False=OFF
        duration: Time to keep LED on (0 = indefinite)
    """
    GPIO.output(RED_LED, state)
    if duration > 0 and state:
        time.sleep(duration)
        GPIO.output(RED_LED, False)

def turn_off_all():
    """Turn off all LEDs and buzzer"""
    GPIO.output(GREEN_LED, False)
    GPIO.output(RED_LED, False)
    GPIO.output(BUZZER, False)

# ==================== LCD FUNCTIONS ====================

def lcd_write(line1="", line2=""):
    """
    Display text on LCD
    Args:
        line1: Text for first row (max 16 chars)
        line2: Text for second row (max 16 chars)
    """
    if not lcd:
        print(f"LCD: {line1} | {line2}")
        return
    
    try:
        # Pad or truncate to 16 chars
        line1 = (line1[:LCD_COLS]).ljust(LCD_COLS)
        line2 = (line2[:LCD_COLS]).ljust(LCD_COLS)
        
        # Clear display
        lcd_write_byte(0x01, 0)
        time_module.sleep(0.01)
        
        # Go to first line
        lcd_write_byte(0x80, 0)
        time_module.sleep(0.01)
        
        # Write first line
        for char in line1:
            lcd_write_byte(ord(char), LCD_RS)
        
        # Go to second line
        lcd_write_byte(0xC0, 0)
        time_module.sleep(0.01)
        
        # Write second line
        for char in line2:
            lcd_write_byte(ord(char), LCD_RS)
            
    except Exception as e:
        print(f"⚠ LCD write error: {e}")

def lcd_known_face(name, roll, status):
    """Display known face on LCD"""
    line1 = f"  {name}"
    line2 = f"{roll} {status}"
    lcd_write(line1, line2)

def lcd_unknown_face():
    """Display unknown face on LCD"""
    line1 = "UNKNOWN FACE"
    line2 = datetime.now().strftime("%H:%M:%S")
    lcd_write(line1, line2)

def lcd_registered_rfid(name, roll):
    """Display registered RFID on LCD"""
    line1 = f"RFID: {name}"
    line2 = roll
    lcd_write(line1, line2)

def lcd_unknown_rfid():
    """Display unknown RFID on LCD"""
    line1 = "Unknown RFID"
    line2 = "Authorization Failed"
    lcd_write(line1, line2)

# ==================== COMBINED RESPONSE FUNCTIONS ====================

def handle_registered(name, roll, status=None):
    """
    Handle registered person detected
    - Green LED ON for 1 second
    - 1 beep
    - Show on LCD
    """
    set_green_led(True, duration=1)
    beep(1, duration=0.2, interval=0.2)
    
    if status:
        lcd_known_face(name, roll, status)
    else:
        lcd_registered_rfid(name, roll)

def handle_unknown():
    """
    Handle unknown person/card detected
    - Red LED ON for 1 second
    - 5 beeps
    - Show on LCD
    """
    set_red_led(True, duration=1)
    beep(5, duration=0.15, interval=0.15)
    lcd_unknown_face()

def cleanup():
    """Clean up GPIO and LCD"""
    turn_off_all()
    if bus:
        try:
            bus.close()
        except:
            pass
    GPIO.cleanup()
    print("✓ Hardware cleaned up")

# ==================== INITIALIZATION ====================

# Initialize LCD on module load
if lcd:
    lcd_init()

