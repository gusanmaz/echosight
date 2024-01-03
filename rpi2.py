import os
import subprocess
import requests
from pydub import AudioSegment
import io
import replicate
from datetime import datetime
from PIL import Image
import cv2

# Configurable parameters
MAX_WIDTH = 1280

def capture_camera_image(output_dir):
    try:
        # Initialize the camera (you might need to install OpenCV for this)
        cap = cv2.VideoCapture(0)

        # Capture a frame from the camera
        ret, frame = cap.read()

        # Generate a timestamp for the captured image
        timestamp = datetime.now().strftime("%d_%m_%Y_%H_%M_%S")

        # Define the image file path and name
        image_file_name = f"{timestamp}_camera_capture.png"
        image_file_path = os.path.join(output_dir, image_file_name)

        # Save the captured frame as an image file
        cv2.imwrite(image_file_path, frame)

        # Release the camera
        cap.release()

        return image_file_path
    except Exception as e:
        print(f"An error occurred while capturing the camera image: {e}")
        return None

def download_and_play_audio(audio_urls, output_dir):
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

        # Save the combined audio file
        timestamp = datetime.now().strftime("%d_%m_%Y_%H_%M_%S")
        audio_file_name = f"{timestamp}_audio_description.wav"
        audio_file_path = os.path.join(output_dir, audio_file_name)
        combined.export(audio_file_path, format="wav")

        # Play the merged audio file
        subprocess.run(["aplay", audio_file_path])

    except Exception as e:
        print(f"An error occurred: {e}")

def process_image(image_path):
    try:
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

            # Split the translated text into substrings of up to 255 characters
            substrings = [translated_output[i:i + 255] for i in range(0, len(translated_output), 255)]

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
    except Exception as e:
        print(f"An error occurred while processing the image: {e}")
        return None

def create_output_directory(base_name):
    dir_name = base_name
    full_dir_path = os.path.join('output', dir_name)
    os.makedirs(full_dir_path, exist_ok=True)
    return full_dir_path

def main():
    try:
        # Create an output directory
        timestamp = datetime.now().strftime("%d_%m_%Y_%H_%M_%S")
        output_dir = create_output_directory(timestamp)

        # Capture an image from the camera
        print("Capturing an image from the camera...")
        image_path = capture_camera_image(output_dir)

        if not image_path:
            raise Exception("Failed to capture the camera image")

        # Process the captured image
        print("Processing the captured image...")
        audio_output = process_image(image_path)

        if not audio_output:
            raise Exception("Failed to process the image or get the audio output")

        # Download and play the audio that describes the image
        print("Playing the audio...")
        download_and_play_audio(audio_output, output_dir)

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
