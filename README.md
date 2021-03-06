# db_panel
This repository contains the source code for the *db_pannel* project.
The goal is to display multiple noise level indications.

It uses *CircuitPython* on a *Adafruit Matrix-portal M4* board, with a 32 x 32 square RGB LED matrix panel.

## Panel assembly
<img src="./doc/assembly_pannel.jpg" height="200"/> <img src="./doc/assembly_matrixportal.jpg" height="200"/> <img src="./doc/assembly_microphone.jpg" height="200"/>

## Installation
- Follow the steps from https://learn.adafruit.com/adafruit-matrixportal-m4
- Copy the `lib`, `bmp` and `code.py` files on the *CIRCUITPY* drive. 


## Repository layout
- The `code.py` contains the application code for the project. 
- `bmp` folder contains the Emoji image used by the main application to indicate the average noise level.
- `circuitpython` folder contains the CircuitPython installation binary for the *Adafruit Matrix-portal M4*
- `lib` folder contains the python libraries used by `code.py`.

## User Manual
The *db_pannel* comes with 4 modes:
- `Current noise level` mode: Indicate the current noise level with a 2 digits number.<br>
<img src="./doc/mode_noise_green.jpg" width="200"/> <img src="./doc/mode_noise_orange.jpg" width="200"/> <img src="./doc/mode_noise_red.jpg" width="200"/>
- `Noise level histogram` mode: Display the noise level in a histogram with the last 32 measurements.
<img src="./doc/mode_histogram.jpg" width="300"/>
- `Noise spectrogram` mode: Display a live spectrum graph, computed with a Fast Fourier Transform operation. This graph is difficult to interpret by itself, and it’s more here for educational purposes.
<img src="./doc/mode_fft.jpg" width="300"/>
- `Noise level selection` menu: Display the current limit *Level* of noise before the graph and numbers turn red in the previous modes. Value range is from 1 to 32.
<img src="./doc/mode_limit.jpg" width="300"/>
- `Emoji selection` menu: Select if an green, orange, red Emoji is displayed every 30 secs, based on the previous measurements. Possible range is `True` (enable) or `False` (disable).
<img src="./doc/mode_emoji.jpg" width="300"/>

<img src="./doc/emoji_green.jpg" width="200"/><img src="./doc/emoji_orange.jpg" width="200"/><img src="./doc/emoji_red.jpg" width="200"/>


The `DOWN` button is used to switch between modes.
The `UP` button is used to interact with the current mode: Increase the `Noise level` in every mode, except on the `Emoji selection` menu where it is used to enable/disable the Emoji.
