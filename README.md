# EchoSight

This project aims to help visually impaired people to understand their surroundings by listening to the description of the images captured by a camera.
There are currently two modes of operation. First one is to capture images from Raspberry Pi Camera by pressing a keyboard button (default: S) to listen voice description of the captured image. Second one is to give an image path or URL to listen voice description of the image.
Second mode of operation is not limited to Raspberry Pi. You provide an image path or URL to listen voice description of the image.

### Pre-requisites (For Usage on Raspberry Pi)

* Boot into Raspberry Pi OS
* To download and create a Raspberry Pi OS on an SD card you could install [Raspberry Pi Imager](https://downloads.raspberrypi.org/imager/imager_latest.exe) on your computer.
* Test whether your Raspberry Pi Camera is working by running

`libcamera-jpeg -o z.jpg`

### Installation

* Obtain Replicate.com API TOKEN
   * For Bash run `echo 'export REPLICATE_API_TOKEN=r8_RAF**********************************' >> ~/.bashrc`
   * For Zsh  run `echo 'export REPLICATE_API_TOKEN=r8_RAF**********************************' >> ~/.zshrc`
* keyboard_path is set by program. But in case of failure to set this value correctly Read https://chat.openai.
  com/share/bd2753d8-0ee3-4963-8e26-9569575470eb to learn how to find you keyboard path to change `keyboard_path` string with correct value.
* `git clone https://github.com/gusanmaz/echosight`
* `cd echosight`
* `python3 -m venv env`
* `source env/bin/activate`
* `pip install -r requirements.txt`

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

Different models may be used in the future. Code may be rewritten to make experimenting with different models easier.

### License
Apache License 2.0
