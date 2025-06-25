import ctypes.wintypes
import random
import time
import cv2
import numpy as np
import ctypes
from ctypes import wintypes
from ctypes import *
import pyautogui
from pyscreeze import screenshot
import threading
import logging
from win import *

import globals

from pynput.keyboard import Controller as Ctrll_1
from pynput.mouse import Controller as Ctrll_2
from pynput.keyboard import Key
from pynput.mouse import Button


from misc import *
from debug_draw import *
from bots import chopping_bot, fishing_bot, owl_bot, megafish_bot

from PIL import ImageGrab

def get_desktop_img():
    desktop_img = screenshot()
    desktop_img = np.array(desktop_img)
    desktop_img = cv2.cvtColor(desktop_img, cv2.COLOR_BGR2RGB)
    return desktop_img


def run_fishing_bot(fishing_bot, frame_img):
    fishing_bot.run(frame_img)

def run_chopping_bot(chopping_bot, frame_img, dt):
    chopping_bot.run(frame_img, dt)

def run_owl_bot(owl_bot, frame_img):
    owl_bot.run(frame_img)

def run_megafish_bot(megafish_bot, frame_img):
    megafish_bot.run(frame_img)

def run_mine_bot():
    print("Staring Mine Bot...")
    print("Ending Mine Bot...")

def do_match(frame_img, template_img, threshold):
    result = cv2.matchTemplate(frame_img, template_img, cv2.TM_CCOEFF_NORMED)
    
    locs_x, locs_y = np.where(result >= threshold)

    return (result, locs_x, locs_y)

mouseX = 0
mouseY = 0
mouseX1 = 0
mouseY1 = 0
mouseState = 0
mouseRead = False
def display1_mousecallback(event,x,y,flags,param):
    global mouseX,mouseY
    global mouseX1,mouseY1
    global mouseRead
    global mouseState
    if event == cv2.EVENT_LBUTTONDOWN:
        mouseRead = False
        if mouseState % 2 == 0:
            mouseX,mouseY = x,y
        else:
            mouseX1,mouseY1 = x,y
        mouseState += 1

def bot_state_string(bot_state):
    if bot_state == 0:
        return "None"
    if bot_state == 1:
        return "Chopping"
    if bot_state == 2:
        return "Fishing"
    if bot_state == 3:
        return "Mining"
    if bot_state == 4:
        return "Catching"
    if bot_state == 5:
        return "Clicker-Owl"
    if bot_state == 6:
        return "Clicker-Fish"
    return "Unknown"

def debug_draw_text_bot_state_options(img_frame, start_pos_x = 50, start_pos_y = 255):
    for i in range(0,100):
        state_string = bot_state_string(i)
        if state_string == "Unknown":
            break

        x_inc = 50
        debug_draw_text(img_frame, state_string + ": " + str(i), (start_pos_x, start_pos_y + x_inc * i))

def debug_draw_text_controls(img_frame):
    controls_keybinds = [
        "´",
        "+",
        "q/esc",
        "w",
        "§/0, f1-9",
        "e",
        ]
    controls_actions = [
        "Resize to max",
        "Resize to selected area",
        "Quit",
        "Toggle Hud",
        "Set bot mode",
        "Toggle Zoom",
        ]

    y_start = 255 + 50
    y_inc = 50

    controls_y_end = y_start
    for i in range(0, controls_keybinds.__len__()):
        keybind = controls_keybinds[i]
        action = controls_actions[i]
        controls_y_end = y_start + y_inc * i
        i = i + 1
        debug_draw_text(img_frame, keybind + ": " + action, (50, controls_y_end))

    debug_draw_text_bot_state_options(img_frame, 50, controls_y_end + y_inc * 2)

def run_bot_by_mode(bot_mode, img_frame, dt):
    if bot_mode == 1:
        run_chopping_bot(chop_bot, img_frame, dt)
    elif bot_mode == 2:
        run_fishing_bot(fish_bot, img_frame)
    elif bot_mode == 3:
        print("None")
        # result, locs_x, locs_y = do_match(img_frame, img_test_mimic)
        # debug_draw_match_results(img_frame, img_test_mimic, locs_x, locs_y)
    elif bot_mode == 4:
        print("None")
        # result, locs_x, locs_y = do_match(img_frame, img_test_mimic)
        # debug_draw_match_results(img_frame, img_test_mimic, locs_x, locs_y)
    elif bot_mode == 5:
        run_owl_bot(feather_bot, img_frame)
    elif bot_mode == 6:
        run_megafish_bot(megafishing_bot, img_frame)

def debug_draw_globals(img_frame):
    global_texts = [
        "State",
        "Accepting Input",
        "show_hud",
        "zoom_factor",
    ]
    global_values = [
        globals.bot_state,
        globals.accepting_input,
        globals.show_hud,
        globals.zoom_factor,
    ]

    y_inc = 50
    y_start = 55
    for i in range(0, global_texts.__len__()):
        debug_draw_text(img_frame, global_texts[i] + ": " + str(global_values[i]), (40, y_start + y_inc * i))

def debug_draw_fps(img_frame, fps):
    debug_draw_text(img_frame, str(int(fps)) + "fps", (1000, 50))

img_test_mimic = cv2.imread("img/test_chest.png", cv2.IMREAD_UNCHANGED)
img_test_ground = cv2.imread("img/test_ground.png", cv2.IMREAD_UNCHANGED)

def HandleFButtonInput():
    if IsKeyboardButtonPressed('§'):
        globals.bot_state = 0
    elif IsKeyboardButtonPressed('f1'):
        globals.bot_state = 1
    elif IsKeyboardButtonPressed('f2'):
        globals.bot_state = 2
        fish_bot.fishing_state.reset()
    elif IsKeyboardButtonPressed('f3'):
        globals.bot_state = 3
    elif IsKeyboardButtonPressed('f4'):
        globals.bot_state = 4
    elif IsKeyboardButtonPressed('f5'):
        globals.bot_state = 5
    elif IsKeyboardButtonPressed('f6'):
        globals.bot_state = 6

def HandleFishBotManualPowerInput():
    if IsKeyboardButtonPressed('§'):
        fish_bot.manual_power = -1
    else:
        button_pressed = -1
        if IsKeyboardButtonPressed('1'):
            button_pressed = 1
        elif IsKeyboardButtonPressed('2'):
            button_pressed = 2
        elif IsKeyboardButtonPressed('3'):
            button_pressed = 3
        elif IsKeyboardButtonPressed('4'):
            button_pressed = 4
        elif IsKeyboardButtonPressed('5'):
            button_pressed = 5
        elif IsKeyboardButtonPressed('6'):
            button_pressed = 6
        elif IsKeyboardButtonPressed('7'):
            button_pressed = 7

        if button_pressed != -1:
            fish_bot.manual_power = button_pressed

if __name__ == "__main__":
    print("Staring Program...")
    window_string = "Bot"

    test_video = None
    if globals.test_video:
        test_video = cv2.VideoCapture("vid/chopping.mkv")
        cv2.namedWindow("test_video", cv2.WINDOW_FULLSCREEN)

    cv2.namedWindow(window_string, cv2.WINDOW_AUTOSIZE)
    cv2.setMouseCallback(window_string, display1_mousecallback)

    chop_bot = chopping_bot.ChoppingBot()
    fish_bot = fishing_bot.FishingBot()
    feather_bot = owl_bot.OwlBot([])
    megafishing_bot = megafish_bot.MegafishBot()
    
    # cv2.imshow("Test", img_test_mimic)

    # region_cap_x0 = 600
    # region_cap_x1 = 2100
    # region_cap_y0 = 465
    # region_cap_y1 = 792

    region_cap_x0 = 0
    region_cap_x1 = 2540
    region_cap_y0 = 0
    region_cap_y1 = 1440

    globals.bot_state = 0
    
    frame_counter = 0
    fps_target = 200
    fps_measurement = -1
    timestamp_last_run = time.perf_counter()
    bRunning = True
    while(bRunning):
        current_time = time.perf_counter()
        dt = current_time - timestamp_last_run
        fps_current = 1.0 / dt
        if frame_counter <= 5:
            fps_measurement = fps_current
        else:
            fps_smoothing = pow(0.1, dt * 60.0 / 1000.0)
            fps_measurement = (fps_measurement * fps_smoothing) + fps_current * (1.0 - fps_smoothing)
        window_title = "fps: " + str(int(fps_measurement))
        cv2.setWindowTitle(window_string, window_title)

        (region_cap_x0, region_cap_x1) = get_min_max(region_cap_x0, region_cap_x1)
        (region_cap_y0, region_cap_y1) = get_min_max(region_cap_y0, region_cap_y1)

        if globals.test_video:
            (test_video_ret, test_video_frame) = test_video.read()
            if not test_video_ret:
                test_video = cv2.VideoCapture("vid/chopping.mkv")
                (test_video_ret, test_video_frame) = test_video.read()

            test_video_frame = cv2_zoom(test_video_frame, 1.34)

        img = ImageGrab.grab(bbox=(region_cap_x0,region_cap_y0,region_cap_x1,region_cap_y1)) #bbox specifies specific region (bbox= x,y,width,height)
        img_np = np.array(img)
        img_frame = cv2.cvtColor(img_np, cv2.COLOR_BGR2RGBA)
        
        run_bot_by_mode(globals.bot_state, img_frame, dt)
        
        if not globals.performance_critical:
            if globals.show_hud:
                # debug_draw_fps(img_frame, fps_measurement)
                if globals.bot_state != 2:
                    debug_draw_globals(img_frame)
                    debug_draw_text_controls(img_frame)

            img_frame = cv2_zoom(img_frame, globals.zoom_factor)

            if globals.show_hud:
                radius = 10
                point0 = (mouseX,mouseY)
                point1 = (mouseX1,mouseY1)
                cv2.circle(img_frame, point0, radius, (0, 0, 255), radius*2)
                cv2.circle(img_frame, point1, radius, (0, 0, 255), radius*2)
                cv2.rectangle(img_frame, point0, point1, (0, 0, 255), radius)

            cv2.imshow(window_string, img_frame)
            if globals.test_video:
                cv2.imshow("test_video", test_video_frame)

            k_press = cv2.waitKey(1) & 0xFF

            if globals.bot_state == 2:
                HandleFishBotManualPowerInput()
                if IsKeyboardButtonPressed('m'):
                    fish_bot.fishing_state.whale_count += 1
                elif IsKeyboardButtonPressed('n'):
                    fish_bot.fishing_state.whale_count += 1
                elif IsKeyboardButtonPressed(','):
                    fish_bot.fishing_state.whale_third_missed = not fish_bot.fishing_state.whale_third_missed

            HandleFButtonInput()

            if (k_press == ord('´')):
                # Reset window size
                desktop_img = get_desktop_img()
                w = desktop_img.shape[1]
                h = desktop_img.shape[0]

                region_cap_x0 = 0
                region_cap_y0 = 0
                region_cap_x1 = w
                region_cap_y1 = h

            if (k_press == ord('+')):
                region_cap_x0 = clamp(mouseX / globals.zoom_factor, 0, 4000)
                region_cap_x1 = clamp(mouseX1 / globals.zoom_factor, 0, 4000)
                region_cap_y0 = clamp(mouseY / globals.zoom_factor, 0, 4000)
                region_cap_y1 = clamp(mouseY1 / globals.zoom_factor, 0, 4000)
                print("X0: %d\nX1: %d\nY0: %d\nY1: %d" % (region_cap_x0, region_cap_x1, region_cap_y0, region_cap_y1))

            if IsKeyboardButtonPressed('q'):
                cv2.destroyWindow(window_string)
                bRunning = False
                break

            if IsKeyboardButtonPressed('w'):
                globals.show_hud = not globals.show_hud
            if IsKeyboardButtonPressed('e'):
                if globals.zoom_factor == 1.0:
                    globals.zoom_factor = 0.5
                else:
                    globals.zoom_factor = 1.0
                

        if IsKeyboardButtonPressed('esc'):
            bRunning = False
        if IsKeyboardButtonPressed('z'):
            globals.accepting_input = not globals.accepting_input
            fish_bot.fishing_state.timestamp_do_input = time.perf_counter()

        timestamp_last_run = current_time
        frame_counter = frame_counter + 1

    print("Shutting down...")
    cv2.destroyAllWindows()


'''

Todo:
- Cull target false positives in the sky by checking vicinity of waterrange
- negative t's causes miss.

'''