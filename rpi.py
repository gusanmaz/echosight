import os
import sys
import subprocess
import requests
from pydub import AudioSegment
import io
import replicate


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


def main(image_path):
    # Check if image_path is provided
    if not image_path:
        print("Please provide an image path.")
        return

    try:
        # Process the provided image
        print("Processing the image...")
        audio_output = process_image(image_path)
        if not audio_output:
            raise Exception("Failed to process the image or get the audio output")

        # Download and play the audio that describes the image
        print("Playing the audio...")
        download_and_play_audio(audio_output)
    except Exception as e:
        print(f"An error occurred in the processing function: {e}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python script.py <image_path>")
        sys.exit(1)

    image_path = sys.argv[1]
    main(image_path)
