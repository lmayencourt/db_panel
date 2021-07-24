import board
import time
import math
import random
import array
import ulab
import ulab.fft
import displayio
import terminalio
from digitalio import DigitalInOut, Pull
from adafruit_display_text import label
from adafruit_matrixportal.matrix import Matrix
from adafruit_debouncer import Debouncer

MATRIX_WIDTH = 32
MATRIX_HEIGHT = 32
DELAY = 1.0

#--------------------------------------------
# Matrix
#--------------------------------------------
matrix = Matrix(width=MATRIX_WIDTH, height=MATRIX_HEIGHT, bit_depth=6)
display = matrix.display
group = displayio.Group()
display.show(group)

bitmap = displayio.Bitmap(display.width, display.height, 8)

palette = displayio.Palette(8)
palette[0] = 0x000000
palette[1] = 0xff0000
palette[2] = 0x00ff00
palette[3] = 0x0000ff
palette[4] = 0xff00ff
palette[5] = 0xffff00
palette[6] = 0x00ffff
palette[7] = 0xffffff

tile_grid = displayio.TileGrid(bitmap, pixel_shader=palette)
group.append(tile_grid)

#--------------------------------------------
# Microphone
#--------------------------------------------
from analogio import AnalogIn

microphone = AnalogIn(board.A0)

# Analog pin returns a value between 0 to 65536
# Microphone returns a value of 1.25v +/- 2vpp,
# range is then 0.25 to 2.25 -> 0 to ~32768
# 0.25 offset is 3276.8.
# scale to to 0-> 1024 (~750 max observed)
def get_audio():
    return max(0,(microphone.value-(65536/4))/32)

def get_audio_applitude(sample_nbr):
    meas_max = 0
    meas_min = 1024
    for i in range(0, sample_nbr):
        measurement = get_audio()
        if measurement > meas_max:
            meas_max = measurement
        if measurement < meas_min:
            meas_min = measurement
    return abs(meas_max-meas_min)

def get_audio_mean(sample_nbr):
    mean = 0
    for i in range(0, sample_nbr):
        mean += get_audio()/sample_nbr
    return mean

def get_audio_positive_only_applitude(sample_nbr):
    mean = 0
    for i in range(0, sample_nbr):
        value = get_audio()-232
        if value < 0:
            mean += (-1*value)/sample_nbr
        else:
            mean += value/sample_nbr
    return mean

fft_size = 256
def get_fft():
    samples_bit = ulab.array([0] * (fft_size))
    start_time = time.monotonic()
    for i in range(0, fft_size):
        samples_bit[i] = int(get_audio()/32)
    print('sampled 256 in: %s' % (time.monotonic() - start_time))
    return ulab.fft.spectrogram(samples_bit)

#--------------------------------------------
# Button
#--------------------------------------------
pin_down = DigitalInOut(board.BUTTON_DOWN)
pin_down.switch_to_input(pull=Pull.UP)
button_down = Debouncer(pin_down)
pin_up = DigitalInOut(board.BUTTON_UP)
pin_up.switch_to_input(pull=Pull.UP)
button_up = Debouncer(pin_up)

def update_display():
    '''Update the matrix display.'''
    #display.auto_refresh = False
    #bitmap.fill(0)
    display.auto_refresh = True

def draw_bar(idx, level, color):
    for x in range(0,MATRIX_HEIGHT-1):
        if x < level-3:
            bitmap[idx, x] = color
        elif x < level-1:
            bitmap[idx, x] = 5
        else:
            bitmap[idx, x] = 0

#--------------------------------------------
# Main
#--------------------------------------------
print('start demo')
text = "demo"
text_area = label.Label(terminalio.FONT, text=text)
text_area.x = 5
text_area.y = 5
display.show(text_area)
time.sleep(1)
display.show(group)
mean = 16
mode = 5
bar = [0] * 32
mode_nbr = mode
while True:
    button_down.update()
    button_up.update()
    if button_up.fell:
        mode = mode + 1
    if button_down.fell:
        mode = mode - 1
    if mode <= 0:
        mode = 0
    elif mode > mode_nbr:
        mode = mode_nbr

    if mode == 0:
        # microphone value scalled to 0->1024 values
        for idx in range(MATRIX_WIDTH-1, 0, -1):
            bar[idx] = bar[idx-1]
            draw_bar(idx, bar[idx], 1)
        bar[0] = get_audio_mean(200)/32
        draw_bar(0, bar[0], 1)
        print('audio mean value: ', bar[0])
    elif mode == 1:
        for idx in range(MATRIX_WIDTH-1, 0, -1):
            bar[idx] = bar[idx-1]
            draw_bar(idx, bar[idx], 2)
        bar[0] = get_audio_applitude(200)/32
        draw_bar(0, bar[0], 2)
        print('audio applitude value: ', bar[0])
    elif mode == 2:
        for idx in range(MATRIX_WIDTH-1, 0, -1):
            bar[idx] = bar[idx-1]
            draw_bar(idx, bar[idx], 3)
        bar[0] = get_audio()/32
        draw_bar(0, bar[0], 3)
        print('audio value: ', bar[0])
    elif mode == 3:
        for idx in range(MATRIX_WIDTH-1, 0, -1):
            bar[idx] = bar[idx-1]
            draw_bar(idx, bar[idx], 2)
        bar[0] = get_audio_positive_only_applitude(200)/2
        draw_bar(0, bar[0], 4)
        print('audio positive only value: ', bar[0])
    elif mode == 4:
        spectrogram = get_fft()
        #print(spectrogram)
        for idx in range(0,256):
            print(f'( {spectrogram[idx]}, {idx})')

        for idx in range(0, MATRIX_WIDTH):
            bar[idx] = 0;
            for ydx in range(0, 8):
                bar[idx] += spectrogram[idx+ydx]/64
            draw_bar(idx, bar[idx], 2)

    elif mode == 5:
        print('(', get_audio(), ', )')
    else:
        print('not a valid mode: ', mode)
    update_display()
    time.sleep(DELAY)