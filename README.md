# EchoSight

EchoSight is designed to assist visually impaired individuals by providing audible descriptions of images captured by a camera. It operates in two modes: one for capturing images using a Raspberry Pi Camera and listening to their voice descriptions, and another for inputting an image path or URL on various operating systems to hear voice descriptions.

## Output Files

The project generates multiple outputs during operation:

- **Image Files**: Captured or downloaded images are saved in the `output` directory.
- **Text Descriptions**: Text descriptions of the images in both English and Turkish are saved as `.txt` files in the `output` directory.
- **Audio Files**: The Turkish voice description of the image is saved as a `.wav` file in the `output` directory.
- **Log Files**: Event logs and errors are recorded and saved in `events.log` files within the respective output subdirectories.

## Configurable Parameters

- **KEY_ACTION**: In `rpi.py`, this is set to 'KEY_S' by default. Modify the `KEY_ACTION` variable to change the key action.
- **CAMERA_DELAY**: In `rpi.py`, the default camera delay is '0.1' seconds. Adjust the `CAMERA_DELAY` variable to change this setting.
- **MAX_WIDTH**: In `image2speech.py`, the maximum image width for resizing is controlled by `MAX_WIDTH`. Alter this parameter as needed.

## Pre-requisites (For Raspberry Pi Usage)

- Ensure Raspberry Pi OS is installed.
- Use [Raspberry Pi Imager](https://downloads.raspberrypi.org/imager/imager_latest.exe) to prepare your SD card.
- Test your Raspberry Pi Camera: `libcamera-jpeg -o z.jpg`.

## Installation

- Obtain your Replicate.com API token:
  - For Bash: `echo 'export REPLICATE_API_TOKEN=your_token_here' >> ~/.bashrc`.
  - For Zsh: `echo 'export REPLICATE_API_TOKEN=your_token_here' >> ~/.zshrc`.
- Set `keyboard_path` correctly if automatic detection fails. Refer to [this guide](https://chat.openai.com/share/bd2753d8-0ee3-4963-8e26-9569575470eb).
- Clone and setup the EchoSight environment:
  ```bash
  git clone https://github.com/gusanmaz/echosight
  cd echosight
  python3 -m venv env
  source env/bin/activate
  pip install -r requirements.txt


### Usage 
**(Raspberry Pi) To capture images from Raspberry Pi Camera by pressing a keyboard button (default: S) to listen 
  voice description of the captured image**

* `python3 rpi.py`

 **(ALL OSes) Give an image path or URL to listen voice description of the image**

* `python3 url2speech.py image_path_or_url`


### Models

This project uses models from https://replicate.com/ to generate voice descriptions of the images. You can find the models used in this project from the links below.

* cogvlm: https://replicate.com/cjwbw/cogvlm
* Seamless Communication: https://replicate.com/cjwbw/seamless-communication
* Coqui XTTS-v2: https://replicate.com/cjwbw/coqui-xtts-v2

Future versions may incorporate different models, and the code could be adapted for easier experimentation with various models.

### Cost

Conservative Cost Estimate: 20 cents per image
Conservative Runtime Estimate: 40 seconds per image to produce audio (excluding time spent for starting the models 
on Replicate.com)

### License
Apache License 2.0
