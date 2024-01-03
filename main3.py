import os
import sys
import subprocess
import threading
import requests
import replicate
from evdev import InputDevice, categorize, ecodes
from PIL import Image
from io import BytesIO
from pydub import AudioSegment
import io
import re

# Global variable to check if a photo is being processed
is_processing = False

# Configurable parameters
KEY_ACTION = 'KEY_S'  # Default key for action, can be changed by the user
CAMERA_DELAY = '0.1'  # Default camera delay in seconds

def download_and_play_audio(audio_urls):
    try:
        # List to store the audio segments
        segments = []

        # Download and append each audio file to the segments list
        for url in audio_urls:
            response = requests.get(url)
            if response.status_code != 200:
                raise Exception("Failed to download the audio file from URL: " + url)

            # Load this audio file into an AudioSegment
            segment = AudioSegment.from_file(io.BytesIO(response.content), format="wav")
            segments.append(segment)

        # Merge all segments
        combined = segments[0]
        for segment in segments[1:]:
            combined += segment

        # Save the combined audio file temporarily
        merged_audio_file_path = "/tmp/merged_temp_audio_file.wav"
        combined.export(merged_audio_file_path, format="wav")

        # Play the merged audio file
        subprocess.run(["aplay", merged_audio_file_path])

        # Optional: Remove the merged audio file after playing
        os.remove(merged_audio_file_path)

    except Exception as e:
        print(f"An error occurred: {e}")

def process_image(image_path):
    with open(image_path, "rb") as image:
        # Run the Bakllava model for image description
        description = replicate.run(
            "cjwbw/cogvlm:a5092d718ea77a073e6d8f6969d5c0fb87d0ac7e4cdb7175427331e1798a34ed",
            input={
                "vqa": False,
                "image": image,
                "query": "Describe this image."
            }
        )

        print("cogvlm model finished\n")
        print("English Description: " + description)

        # Run the Seamless Communication model for translation
        translated_output = replicate.run(
            "cjwbw/seamless_communication:668a4fec05a887143e5fe8d45df25ec4c794dd43169b9a11562309b2d45873b0",
            input={
                "task_name": "T2TT (Text to Text translation)",
                "input_text": description,
                "input_text_language": "English",
                "target_language_text_only": "Turkish",
            }
        )

        translated_output = translated_output['text_output']

        print("Seamless Model finished\n")
        print("Turkish Description: " + translated_output)


        # Split the translated text into substrings of up to 255 characters
        substrings = [translated_output[i:i+255] for i in range(0, len(translated_output), 255)]
        for i, substring in enumerate(substrings):
            print(f"Substring {i}: {substring}")

        audio_urls = []
        for substring in substrings:
            # Run the xtts-v2 model on each substring
            output = replicate.run(
                "lucataco/xtts-v2:684bc3855b37866c0c65add2ff39c78f3dea3f4ff103a436465326e0f438d55e",
                input={
                    "text": substring,
                    "speaker": "https://replicate.delivery/pbxt/Jt79w0xsT64R1JsiJ0LQRL8UcWspg5J4RFrU6YwEKpOT1ukS/male.wav",
                    "language": "tr",
                    "cleanup_voice": True
                }
            )
            audio_urls.append(output)

        return audio_urls

def capture_and_process():
    global is_processing
    if is_processing:
        print("Previous image processing discarded.")
        return

    is_processing = True

    # Capture the image using libcamera-jpeg with configurable delay
    subprocess.run(['libcamera-jpeg', '-t', f'{CAMERA_DELAY}sec', '-o', 'out.jpg'])

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

def find_keyboard_device():
    # Execute the ls command and get the output
    result = subprocess.run(['ls', '/dev/input/by-id/'], capture_output=True, text=True)

    # Check if the command executed successfully
    if result.returncode != 0:
        raise Exception("Failed to execute ls command")

    # Use regular expression to find keyboard device names
    # This looks for devices containing 'kbd' or 'keyboard' in their name
    matches = re.findall(r'usb-.*(?:kbd|keyboard)', result.stdout)
    if not matches:
        raise Exception("No keyboard device found")

    return '/dev/input/by-id/' + matches[0]

def handle_key_presses(keyboard):
    for event in keyboard.read_loop():
        if event.type == ecodes.EV_KEY:
            key_event = categorize(event)
            if key_event.keystate == key_event.key_up and key_event.keycode == KEY_ACTION:
                print(f"{KEY_ACTION} key pressed, capturing image...")
                threading.Thread(target=capture_and_process).start()

try:
    keyboard_path = find_keyboard_device()
    keyboard = InputDevice(keyboard_path)
    print("Listening for key presses on device:", keyboard)
    handle_key_presses(keyboard)
except Exception as e:
    print(f"An error occurred: {e}")

