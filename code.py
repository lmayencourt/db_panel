import board
import time
import math
import random
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
DELAY = 0.2

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
# scale to to 0-> 1024
def get_audio():
    return (microphone.value-3276.8)/32

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
mode = 0
bar = [0] * 32
while True:
    button_down.update()
    button_up.update()
    if button_up.fell:
        mode = mode + 1
    if button_down.fell:
        mode = mode - 1
    if mode <= 0:
        mode = 0
    elif mode > 2:
        mode = 2

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
        value = get_audio()
        draw_bar(0, value/32, 3)
        print('audio value: ', value)
    else:
        print('not a valid mode: ', mode)
    update_display()
    time.sleep(DELAY)