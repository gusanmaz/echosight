import os
import sys
import subprocess
import threading
import requests
import replicate
from evdev import InputDevice, categorize, ecodes
from PIL import Image
from io import BytesIO

# Global variable to check if a photo is being processed
is_processing = False

# Replace XYZ with you API TOKEN
os.environ['REPLICATE_API_TOKEN'] = 'XYZ'

def download_and_play_audio(json_output):
    try:
        # Extract the audio URL from the JSON output
        text_output = json_output.get('text_output')
        print("Turkish: " + text_output)
        audio_url = json_output.get('audio_output')
        if not audio_url:
            raise ValueError("Audio URL not found in the JSON output")

        # Download the audio file
        response = requests.get(audio_url)
        if response.status_code != 200:
            raise Exception("Failed to download the audio file")

        # Save the audio file temporarily
        audio_file_path = "/tmp/temp_audio_file.wav"
        with open(audio_file_path, 'wb') as audio_file:
            audio_file.write(response.content)

        # Play the audio file
        subprocess.run(["aplay", audio_file_path])

        # Optional: Remove the audio file after playing
        os.remove(audio_file_path)

    except Exception as e:
        print(f"An error occurred: {e}")

def process_image(image_path):
    with open(image_path, "rb") as image:
        # Run the Bakllava model for image description
        description = replicate.run(
            "lucataco/bakllava:452b2fa0b66d8acdf40e05a7f0af948f9c6065f6da5af22fce4cead99a26ff3d",
            input={
                "image": image,
                "prompt": "Describe this image",
                "max_sequence": 512
            }
        )

        print("Bakllava model finished\n")
        print("English Description: " + description)

        # Run the Seamless Communication model for translation and text-to-speech
        output = replicate.run(
            "cjwbw/seamless_communication:668a4fec05a887143e5fe8d45df25ec4c794dd43169b9a11562309b2d45873b0",
            input={
                "task_name": "T2ST (Text to Speech translation)",
                "input_text": description,
                "input_text_language": "English",
                "max_input_audio_length": 150,
                "target_language_with_speech": "Turkish"
            }
        )
        print("Seamless Communication model finished\n")
        return output


def capture_and_process():
    global is_processing
    if is_processing:
        print("Previous image processing discarded.")
        return

    is_processing = True

    # Capture the image using libcamera-jpeg
    os.system('libcamera-jpeg -t 0.1sec -o out.jpg')

    # Process the captured image
    try:
        print("Processing the image...")
        audio_output = process_image('out.jpg')
        if not audio_output:
            raise Exception("Failed to process the image or get the audio output")

        # Download and play the audio that describes the image
        print("Playing the audio...")
        download_and_play_audio(audio_output)
    except Exception as e:
        print(f"An error occurred in the processing function: {e}")

    is_processing = False

def handle_key_presses(keyboard):
    for event in keyboard.read_loop():
        if event.type == ecodes.EV_KEY:
            key_event = categorize(event)
            if key_event.keystate == key_event.key_up and key_event.keycode == 'KEY_S':
                print("S key pressed, capturing image...")
                # Run capture and process in a separate thread
                threading.Thread(target=capture_and_process).start()

# Change this to your specific device
# Read here: https://chat.openai.com/share/bd2753d8-0ee3-4963-8e26-9569575470eb
keyboard_path = '/dev/input/by-id/usb-Apple_Inc._Magic_Keyboard_XYZ-if01-event-kbd'

try:
    # Create an InputDevice object for the keyboard
    keyboard = InputDevice(keyboard_path)

    print("Listening for key presses on device:", keyboard)
    handle_key_presses(keyboard)
except Exception as e:
    print(f"An error occurred: {e}")

#"target_language_text_only": "Norwegian Nynorsk",
