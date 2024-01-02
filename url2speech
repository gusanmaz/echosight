import requests
import subprocess
import os
import replicate
import sys

from PIL import Image
from io import BytesIO

os.environ['REPLICATE_API_TOKEN'] = 'abc'

def download_image(image_url):
    try:
        # Send a GET request to the image URL
        response = requests.get(image_url)
        if response.status_code != 200:
            raise Exception("Failed to download the image")

        # Open the image using PIL
        image = Image.open(BytesIO(response.content))

        # Resize the image if its width is greater than 1028 pixels
        max_width = 1028
        if image.width > max_width:
            # Calculate the new height to maintain the aspect ratio
            new_height = int((max_width / image.width) * image.height)
            image = image.resize((max_width, new_height), Image.LANCZOS)

        # Define the path where the image will be saved
        image_path = "out.png"

        # Save the image as PNG
        image.save(image_path, format='PNG')

        # Return the path to the saved image
        return image_path

    except Exception as e:
        print(f"An error occurred: {e}")
        return None

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

        # Run the Seamless Communication model for translation and text-to-speech
        output = replicate.run(
            "cjwbw/seamless_communication:668a4fec05a887143e5fe8d45df25ec4c794dd43169b9a11562309b2d45873b0",
            input={
                "task_name": "T2ST (Text to Speech translation)",
                "input_text": description,
                "input_text_language": "English",
                "max_input_audio_length": 60,
                "target_language_text_only": "Norwegian Nynorsk",
                "target_language_with_speech": "Turkish"
            }
        )
        return output

def download_and_play_audio(json_output):
    try:
        # Extract the audio URL from the JSON output
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


def main():
    if len(sys.argv) != 2:
        print("Usage: python script_name.py <image_url>")
        sys.exit(1)

    image_url = sys.argv[1]

    try:
        # Download the image from the URL
        print("Downloading the image...")
        image_path = download_image(image_url)
        if not image_path:
            raise Exception("Failed to download or process the image")

        # Process the image to get the description and convert it to audio
        print("Processing the image...")
        audio_output = process_image(image_path)
        if not audio_output:
            raise Exception("Failed to process the image or get the audio output")

        # Download and play the audio that describes the image
        print("Playing the audio...")
        download_and_play_audio(audio_output)

    except Exception as e:
        print(f"An error occurred in the main function: {e}")

# Start the main function
if __name__ == "__main__":
    main()
