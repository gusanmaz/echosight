import evdev
from evdev import InputDevice, categorize, ecodes

# Change this to your specific device
keyboard_path = '/dev/input/by-id/usb-Apple_Inc._Magic_Keyboard_XYZ-if01-event-kbd'

# Create an InputDevice object for the keyboard
keyboard = InputDevice(keyboard_path)

print("Listening for key presses on device:", keyboard)

# Loop to capture keypresses
for event in keyboard.read_loop():
    if event.type == ecodes.EV_KEY:
        key_event = categorize(event)
        if key_event.keystate == key_event.key_up:
            print(f"Key {key_event.keycode} released")
