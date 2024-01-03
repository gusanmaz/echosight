import os
import sys
import subprocess
import requests
from pydub import AudioSegment
import io
import platform
import tempfile
import shutil
import replicate
from datetime import datetime
import urllib.parse
from PIL import Image
import logging  # Import the logging module

# Configurable parameter
MAX_WIDTH = 1280

def setup_logging(base_name):
    """Set up logging to file in the output directory."""
    log_file = os.path.join('output', base_name, 'events.log')
    logging.basicConfig(filename=log_file, level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s',
                        datefmt='%d-%m-%Y %H:%M:%S')

def play_audio(file_path):
    logging.info(f"Playing audio file: {file_path}")
    os_name = platform.system()
    if os_name == 'Linux':
        subprocess.run(['aplay', file_path])
    elif os_name == 'Darwin':  # macOS
        subprocess.run(['afplay', file_path])
    elif os_name == 'Windows':
        subprocess.run(['wmplayer', file_path], shell=True)
    else:
        raise Exception(f"Unsupported operating system: {os_name}")

def download_and_play_audio(audio_urls, audio_file_name):
    try:
        segments = []
        for url in audio_urls:
            logging.info(f"Downloading audio from URL: {url}")
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
        logging.info(f"Audio file saved: {audio_file_path}")
        play_audio(audio_file_path)

    except Exception as e:
        logging.error(f"An error occurred in download_and_play_audio: {e}")
        print(f"An error occurred: {e}")

def extract_model_name(model_string):
    return model_string.split('/')[-1].split(':')[0]

def resize_image(input_path, output_path, max_width=1028):
    try:
        with Image.open(input_path) as img:
            if img.width > max_width:
                # Calculate the new height to maintain the aspect ratio
                new_height = int((max_width / img.width) * img.height)
                img = img.resize((max_width, new_height), Image.LANCZOS)

                # Save the resized image
                img.save(output_path, format='PNG')
                logging.info(f"Image resized and saved: {output_path}")
                return True
        return False
    except Exception as e:
        logging.error(f"An error occurred in resize_image: {e}")
        print(f"An error occurred while resizing the image: {e}")
        return False

def process_image(image_path, timestamp):
    try:
        cogvlm_model_str = "cjwbw/cogvlm:a5092d718ea77a073e6d8f6969d5c0fb87d0ac7e4cdb7175427331e1798a34ed"

        # Open the image file for reading in binary mode
        with open(image_path, "rb") as image_file:
            logging.info(f"Processing image for description: {image_path}")
            description = replicate.run(cogvlm_model_str, input={"vqa": False, "image": image_file, "query": "Describe this image."})

        seamless_model_str = "cjwbw/seamless_communication:668a4fec05a887143e5fe8d45df25ec4c794dd43169b9a11562309b2d45873b0"
        translated_output = replicate.run(seamless_model_str, input={"task_name": "T2TT (Text to Text translation)", "input_text": description, "input_text_language": "English", "target_language_text_only": "Turkish"})
        translated_output = translated_output['text_output']

        english_file = f"{timestamp}_{extract_model_name(cogvlm_model_str)}_english.txt"
        turkish_file = f"{timestamp}_{extract_model_name(seamless_model_str)}_turkish.txt"

        with open(os.path.join(output_dir, english_file), 'w') as file:
            file.write(description)
        logging.info(f"English description saved: {english_file}")
        with open(os.path.join(output_dir, turkish_file), 'w') as file:
            file.write(translated_output)
        logging.info(f"Turkish translation saved: {turkish_file}")

        xtts_model_str = "lucataco/xtts-v2:684bc3855b37866c0c65add2ff39c78f3dea3f4ff103a436465326e0f438d55e"
        audio_file_name = f"{timestamp}_{extract_model_name(xtts_model_str)}.wav"

        substrings = [translated_output[i:i+255] for i in range(0, len(translated_output), 255)]
        audio_urls = []
        for substring in substrings:
            output = replicate.run(xtts_model_str, input={"text": substring, "speaker": "https://replicate.delivery/pbxt/Jt79w0xsT64R1JsiJ0LQRL8UcWspg5J4RFrU6YwEKpOT1ukS/male.wav", "language": "tr", "cleanup_voice": True})
            audio_urls.append(output)

        return audio_urls, audio_file_name
    except Exception as e:
        logging.error(f"An error occurred in process_image: {e}")
        print(f"An error occurred while processing the image: {e}")
        return None, None

def download_image(url, timestamp):
    try:
        logging.info(f"Downloading image from URL: {url}")
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            original_file_name = f"{timestamp}_{os.path.basename(urllib.parse.urlparse(url).path)}"
            original_path = os.path.join(output_dir, original_file_name)

            with open(original_path, 'wb') as out_file:
                shutil.copyfileobj(response.raw, out_file)
            logging.info(f"Image downloaded and saved: {original_path}")

            file_root, file_extension = os.path.splitext(original_file_name)
            resized_file_name = f"{file_root}_small{file_extension}"
            resized_path = os.path.join(output_dir, resized_file_name)

            if resize_image(original_path, resized_path, MAX_WIDTH):
                return resized_path
            else:
                return original_path

        else:
            raise Exception("Failed to download image from URL")

    except Exception as e:
        logging.error(f"An error occurred in download_image: {e}")
        print(f"An error occurred: {e}")
        return None

def create_output_directory(base_name):
    dir_name = base_name
    full_dir_path = os.path.join('output', dir_name)
    os.makedirs(full_dir_path, exist_ok=True)
    logging.info(f"Output directory created: {full_dir_path}")
    return full_dir_path

def get_base_name(input_path):
    if input_path.startswith('http://') or input_path.startswith('https://'):
        path = urllib.parse.urlparse(input_path).path
        return os.path.splitext(os.path.basename(path))[0]
    else:
        return os.path.splitext(os.path.basename(input_path))[0]

def main(image_input):
    if not image_input:
        print("Please provide an image path or URL.")
        return

    global output_dir
    base_name = get_base_name(image_input)
    output_dir = create_output_directory(base_name)
    timestamp = datetime.now().strftime("%d_%m_%Y_%H_%M")

    setup_logging(base_name)  # Set up logging

    try:
        if image_input.startswith('http://') or image_input.startswith('https://'):
            logging.info("Downloading image")
            print("Downloading image...")
            image_path = download_image(image_input, timestamp)
        else:
            image_path = image_input
            timestamped_image_name = f"{timestamp}_{os.path.basename(image_path)}"
            shutil.copy(image_path, os.path.join(output_dir, timestamped_image_name))

        logging.info("Processing the image")
        print("Processing the image...")
        audio_output, audio_file_name = process_image(image_path, timestamp)

        if not audio_output or not audio_file_name:
            raise Exception("Failed to process the image or get the audio output")

        logging.info("Playing the audio")
        print("Playing the audio...")
        download_and_play_audio(audio_output, audio_file_name)

    except Exception as e:
        logging.error(f"An error occurred in main: {e}")
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python script.py <image_path_or_url>")
        sys.exit(1)

    image_input = sys.argv[1]
    main(image_input)
