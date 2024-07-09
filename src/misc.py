import random
import cv2
import numpy as np
from pynput.keyboard import Key
from pynput.mouse import Button
import time
import keyboard
import globals

from pynput.mouse import Controller as Ctrll_Mouse
from pynput.keyboard import Controller as Ctrll_Keyboard

def clamp(val, in_min, in_max):
    val = min(max(val, in_min), in_max)
    return val

def gather_match_results(template_w, template_h, locs_x, locs_y, group_threshold):
    rectangles = []
    for (x,y) in zip(locs_x, locs_y):
        rectangles.append((int(x), int(y), int(template_w), int(template_h)))
        # rectangles.append((int(x), int(y), int(x+template_w), int(y+template_h)))
    rectangles, weights = cv2.groupRectangles(rectangles, 1, group_threshold)

    return rectangles

def filter_locs(result, threshold):
    (locs_y, locs_x) = np.where(result >= threshold)

    return (locs_x, locs_y)
    
    
def randFloat(start, end):
    return (float(random.randrange(0, 100)) / 100.0) * (end - start) + start

def SpaceDown():
    keyboard_controller = Ctrll_Keyboard()
    keyboard_controller.press(Key.space)

def SpaceUp():
    keyboard_controller = Ctrll_Keyboard()
    keyboard_controller.release(Key.space)

def PressSpace():
    rand_sleep_base = 0.001
    rand_jitter_range = 0.002
    SpaceDown()
    print("Space Pressed")
    sleep_duration = rand_sleep_base + randFloat(-rand_jitter_range, rand_jitter_range)
    time.sleep(sleep_duration)
    SpaceUp()
    sleep_duration = rand_sleep_base + randFloat(-rand_jitter_range, rand_jitter_range)
    time.sleep(sleep_duration)

def IsKeyboardButtonPressed(button_str):
    return keyboard.is_pressed(button_str)

def MouseClickPosition(pos_xy):
    mouse_controller = Ctrll_Mouse()
    mouse_controller.position = (int(pos_xy[0]), int(pos_xy[1]))
    mouse_controller.click(Button.left)

def rect_center(rect):
    center_x = rect[0] + 0.5 * rect[2]
    center_y = rect[1] + 0.5 * rect[3]
    return (center_x, center_y)

def stall(seconds):
    timestamp_start = time.perf_counter()

    while(True):
        timestamp_now = time.perf_counter()
        elapsed = timestamp_now - timestamp_start
        if elapsed >= seconds:
            break

def cv2_zoom_at(img, zoom=1, angle=0, coord=None):
    cy, cx = [ i/2 for i in img.shape[:-1] ] if coord is None else coord[::-1]
    
    rot_mat = cv2.getRotationMatrix2D((cx,cy), angle, zoom)
    result = cv2.warpAffine(img, rot_mat, img.shape[1::-1], flags=cv2.INTER_LINEAR)
    
    return result

def cv2_zoom(img, zoom=1):
    return cv2.resize(img, None, fx=zoom, fy=zoom)

def get_min_max(min_val, max_val):
    temp = min_val
    min_val = min(min_val, max_val)
    max_val = max(temp, max_val)

    return (min_val, max_val)

def is_val_within_range(val, range):
    return val >= range[0] and val < range[1]