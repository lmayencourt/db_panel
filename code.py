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
import adafruit_imageload
from adafruit_matrixportal.matrix import Matrix
from adafruit_debouncer import Debouncer

#--------------------------------------------
# Globals
#--------------------------------------------
MATRIX_WIDTH = 32
MATRIX_HEIGHT = 32
DELAY = 0.1

# Default threshold value.
# Modify this number if you want another starting threshold.
# Range: 1 -> 31
threshold = 12
mode = 0
old_mode = 5
mode_nbr = old_mode
# Defaulte emoji enable
# Modify this variable to set enable/disable by default the emoji face.
# Possible values: 'True' or 'False
emoji = True
emoji_average = 0
emoji_average_count = 0
emoji_time = time.monotonic()
# Default emoji face interval in seconds.
# Modify this value if you want the emoji to be display at another interval.
# Range: 5 -> 300 secs
emoji_interval = 20

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

bar = [0] * 32

def update_display():
    '''Update the matrix display.'''
    #display.auto_refresh = False
    #bitmap.fill(0)
    display.auto_refresh = True

def draw_text(text, x=14, y=12, color=0xffffff):
    display.rotation=180
    text_area = label.Label(terminalio.FONT, text=text, x=x, y=y, color=color)
    display.show(text_area)

def draw_bitmap(image_name):
    display.rotation=180
    bitmap, palette = adafruit_imageload.load(image_name,
                                         bitmap=displayio.Bitmap,
                                         palette=displayio.Palette)

    # Make the color at index 0 show as transparent
    palette.make_transparent(0)
    # Create a TileGrid to hold the bitmap
    tile_grid = displayio.TileGrid(bitmap, pixel_shader=palette)

    # Create a Group to hold the TileGrid
    group = displayio.Group()

    # Add the TileGrid to the Group
    group.append(tile_grid)

    # Add the Group to the Display
    display.show(group)

def draw_graph():
    display.rotation=0
    display.show(group)

def draw_bar(idx, level, color):
    for x in range(0,MATRIX_HEIGHT-1):
        if x < level:
            if x < threshold-3:
                bitmap[idx, x] = color
            elif x < threshold:
                bitmap[idx, x] = 5
            else:
                bitmap[idx, x] = 1
        else:
            bitmap[idx, x] = 0

def draw_historygram(value, color=2):
    draw_graph()
    for idx in range(MATRIX_WIDTH-1, 0, -1):
        bar[idx] = bar[idx -1]
        draw_bar(idx, bar[idx], color)
    bar[0] = value
    draw_bar(0, bar[0], 2)
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
    #return microphone.value

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

def get_audio_max(sample_nbr):
    meas_max = 0
    for i in range(0, sample_nbr):
        measurement = get_audio()
        if measurement > meas_max:
            meas_max = measurement
    return meas_max/32

fft_size = 256
def get_fft():
    samples_bit = ulab.array([0] * (fft_size))
    start_time = time.monotonic()
    for i in range(0, fft_size):
        samples_bit[i] = int(get_audio()/32)
    print('sampled 256 in: %s' % (time.monotonic() - start_time))
    return ulab.fft.spectrogram(samples_bit)

def get_cumulated_fft_values(sensitivity):
    spectrogram = get_fft()
    accumulator = 0
    for idx in range(1, fft_size):
        accumulator += spectrogram[idx]/(fft_size*sensitivity)
    return accumulator

#--------------------------------------------
# Button
#--------------------------------------------
pin_down = DigitalInOut(board.BUTTON_DOWN)
pin_down.switch_to_input(pull=Pull.UP)
button_down = Debouncer(pin_down)
pin_up = DigitalInOut(board.BUTTON_UP)
pin_up.switch_to_input(pull=Pull.UP)
button_up = Debouncer(pin_up)

#--------------------------------------------
# Main
#--------------------------------------------
print('start title')
draw_text('Affi\ndB', x= 2, y=4)
time.sleep(1.5)
draw_graph()
print('start')
    
while True:
    button_down.update()
    button_up.update()
    if mode != 4:
        if button_up.fell:
            threshold = threshold + 1
        if threshold <= 1:
            threshold = 1
        elif threshold > 31:
            threshold = 1
    else:
        if button_up.fell:
            emoji = not emoji
    
    if button_down.fell:
        mode = mode + 1
    if mode <= 0:
        mode = 0
    elif mode >= mode_nbr:
        mode = 0

    if mode != old_mode:
        draw_text(f'Mode:\n{str(mode)}', x=2, y=4)
        time.sleep(0.8)
        draw_graph()
        old_mode = mode

    value = 0
    if mode == 0:
        # Print cumulated FFT values
        value = get_cumulated_fft_values(1)
        if value < threshold-3:
            draw_text(f'Vol:\n  {str(int(value))}', x=2, y=4, color=0x00ff00)
        elif value < threshold:
            draw_text(f'Vol:\n  {str(int(value))}', x=2, y=4, color=0xffff00)
        else:
            draw_text(f'Vol:\n  {str(int(value))}', x=2, y=4, color=0xff0000)
    elif mode == 1:
        # Draw cumulated FFT values historigram
        value = get_cumulated_fft_values(2)
        draw_historygram(value)
    elif mode == 2:
        # Draw FFT spectrogram
        draw_graph()
        spectrogram = get_fft()

        for idx in range(0, MATRIX_WIDTH):
            bar[idx] = 0;
            for ydx in range(0, 8):
                bar[idx] += spectrogram[idx+ydx]/64
            draw_bar(idx, bar[idx], 2)
    elif mode == 3:
        # Change threshold
        draw_text(f'Limit\n{threshold}', x=0, y=4)
    elif mode == 4:
        draw_text(f'Emoji\n{emoji}', x=1, y=4)
    else:
        print('Unvalid mode')

    emoji_average += value
    emoji_average_count += 1
    if emoji and mode < 3:
        if emoji_time+emoji_interval < time.monotonic():
            emoji_average = emoji_average / emoji_average_count
            if emoji_average < threshold-3:
                draw_bitmap("bmp/green.bmp")
            elif emoji_average < threshold:
                draw_bitmap("bmp/orange.bmp")
            else:
                draw_bitmap("bmp/red.bmp")
            time.sleep(3)
            emoji_time = time.monotonic()
            emoji_average = 0
            emoji_average_count = 0
        else:
            print(f'emoji {emoji_average}/{emoji_average_count} due in {emoji_time}, now: {time.monotonic()}')

    print(f'threshold {threshold}')
    update_display()
    time.sleep(DELAY)