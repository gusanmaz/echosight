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
from datetime import datetime
import logging

# Global variable to check if a photo is being processed
is_processing = False

# Configurable parameters
KEY_ACTION = 'KEY_S'  # Default key for action, can be changed by the user
CAMERA_DELAY = '0.1'  # Default camera delay in seconds

# Set up logging
logging.basicConfig(filename='camera_script.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    datefmt='%d-%m-%Y %H:%M:%S')

def create_output_directory():
    dir_name = datetime.now().strftime("%d_%m_%Y_%H_%M")
    full_dir_path = os.path.join('output', dir_name)
    os.makedirs(full_dir_path, exist_ok=True)
    logging.info(f"Output directory created: {full_dir_path}")
    return full_dir_path

def download_and_play_audio(audio_urls, audio_file_name, output_dir):
    try:
        segments = []
        for url in audio_urls:
            response = requests.get(url)
            if response.status_code != 200:
                raise Exception("Failed to download the audio file from URL: " + url)

            segment = AudioSegment.from_file(io.BytesIO(response.content), format="wav")
            segments.append(segment)

        combined = segments[0]
        for segment in segments[1:]:
            combined += segment

        audio_file_path = os.path.join(output_dir, audio_file_name)
        combined.export(audio_file_path, format='wav')
        logging.info(f"Audio file created: {audio_file_path}")
        subprocess.run(["aplay", audio_file_path])

    except Exception as e:
        logging.error(f"Error in download_and_play_audio: {e}")
        print(f"An error occurred: {e}")

def process_image(image_path, output_dir):
    try:
        with open(image_path, "rb") as image:
            description = replicate.run(
                "cjwbw/cogvlm:a5092d718ea77a073e6d8f6969d5c0fb87d0ac7e4cdb7175427331e1798a34ed",
                input={"vqa": False, "image": image, "query": "Describe this image."}
            )

            english_file = os.path.join(output_dir, "description_english.txt")
            with open(english_file, 'w') as file:
                file.write(description)
            logging.info(f"English description saved: {english_file}")

            translated_output = replicate.run(
                "cjwbw/seamless_communication:668a4fec05a887143e5fe8d45df25ec4c794dd43169b9a11562309b2d45873b0",
                input={
                    "task_name": "T2TT (Text to Text translation)",
                    "input_text": description,
                    "input_text_language": "English",
                    "target_language_text_only": "Turkish",
                }
            )['text_output']

            turkish_file = os.path.join(output_dir, "description_turkish.txt")
            with open(turkish_file, 'w') as file:
                file.write(translated_output)
            logging.info(f"Turkish translation saved: {turkish_file}")

            substrings = [translated_output[i:i+255] for i in range(0, len(translated_output), 255)]
            audio_urls = []
            for substring in substrings:
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

            audio_file_name = "description_audio.wav"
            return audio_urls, audio_file_name
    except Exception as e:
        logging.error(f"Error in process_image: {e}")
        print(f"An error occurred: {e}")

def capture_and_process():
    global is_processing
    if is_processing:
        logging.warning("Previous image processing discarded.")
        print("Previous image processing discarded.")
        return

    is_processing = True
    output_dir = create_output_directory()
    logging.info("Starting image capture and processing")

    try:
        subprocess.run(['libcamera-jpeg', '-t', f'{CAMERA_DELAY}sec', '-o', 'out.jpg'])
        image_path = os.path.join(output_dir, 'captured_image.jpg')
        os.rename('out.jpg', image_path)

        logging.info("Image captured and processing started")
        print("Processing the image...")
        audio_output, audio_file_name = process_image(image_path, output_dir)

        if not audio_output or not audio_file_name:
            raise Exception("Failed to process the image or get the audio output")

        print("Playing the audio...")
        download_and_play_audio(audio_output, audio_file_name, output_dir)
    except Exception as e:
        logging.error(f"An error occurred in capture_and_process: {e}")
        print(f"An error occurred in the processing function: {e}")

    is_processing = False
    logging.info("Image processing completed")

def find_keyboard_device():
    try:
        result = subprocess.run(['ls', '/dev/input/by-id/'], capture_output=True, text=True)
        if result.returncode != 0:
            raise Exception("Failed to execute ls command")

        matches = re.findall(r'usb-.*(?:kbd|keyboard)', result.stdout)
        if not matches:
            raise Exception("No keyboard device found")

        keyboard_device = '/dev/input/by-id/' + matches[0]
        logging.info(f"Keyboard device found: {keyboard_device}")
        return keyboard_device
    except Exception as e:
        logging.error(f"Error in find_keyboard_device: {e}")
        raise

def handle_key_presses(keyboard):
    try:
        for event in keyboard.read_loop():
            if event.type == ecodes.EV_KEY:
                key_event = categorize(event)
                if key_event.keystate == key_event.key_up and key_event.keycode == KEY_ACTION:
                    logging.info(f"{KEY_ACTION} key pressed, initiating capture and process")
                    print(f"{KEY_ACTION} key pressed, capturing image...")
                    threading.Thread(target=capture_and_process).start()
    except Exception as e:
        logging.error(f"Error in handle_key_presses: {e}")
        print(f"An error occurred: {e}")

try:
    keyboard_path = find_keyboard_device()
    keyboard = InputDevice(keyboard_path)
    print("Listening for key presses on device:", keyboard)
    handle_key_presses(keyboard)
except Exception as e:
    logging.error(f"Top-level error: {e}")
    print(f"An error occurred: {e}")
