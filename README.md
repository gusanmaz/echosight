### Test

`libcamera-jpeg -o z.jpg`

### Installation & Usage

* Boot into Raspberry Pi OS
* To download and create a Raspberry Pi OS on an SD card you could install [Raspberry Pi Imager](https://downloads.raspberrypi.org/imager/imager_latest.exe) on your computer.
* Obtain Replicate.com API TOKEN
* Change `API TOKEN` and `keyboard path` values in `main.py` accordingly.
* Read https://chat.openai.com/share/bd2753d8-0ee3-4963-8e26-9569575470eb to learn how to find you keyboard path to change `keyboard_path` string with correct value.

* `git clone https://github.com/gusanmaz/echosight`
* `cd echosight`
* `python3 -m venv myenv`
* `source myenv/bin/activate`
* `pip install -r requirements.txt`
* `python3 main.py`
