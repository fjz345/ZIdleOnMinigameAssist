from decimal import Decimal
import math
import time
import cv2
from misc import *
import globals
from debug_draw import *

class Grid3x4:
    def __init__(self):
        self.grid_points = [(0,0),(1,0),(2,0),(3,0),
                            (0,1),(1,1),(2,1),(3,1),
                            (0,2),(1,2),(2,2),(3,2)]
        
        self.size_xy = (1,1)
        self.offset_xy = (20,10)

    def to_2d(self, index0to11):
        column_size = 4
        x = index0to11 % column_size
        y = index0to11 / column_size
        return (x,y)

    def to_1d(self, row0to2, column0to3):
        column_size = 4
        return row0to2 + column_size * column0to3

    def get_point_position(self, nr_row, nr_column):
        index1d = self.to_1d(int(nr_row)-1, int(nr_column)-1)
        x = self.offset_xy[0] + self.size_xy[0] * self.grid_points[index1d][0]
        y = self.offset_xy[1] + self.size_xy[1] * self.grid_points[index1d][1]
        return (x,y)


img_megafish_golden_tap = cv2.imread("img/megafish/megafish_tap_golden_fish.png", cv2.IMREAD_UNCHANGED)
img_megafish_golden_tap = cv2.cvtColor(img_megafish_golden_tap, cv2.COLOR_RGB2RGBA)
img_megafish_golden_catch = cv2.imread("img/megafish/mega_fish_golden_catch.png", cv2.IMREAD_UNCHANGED)
img_megafish_golden_catch = cv2.cvtColor(img_megafish_golden_catch, cv2.COLOR_RGB2RGBA)

img_megafish_target_01_active = cv2.imread("img/megafish/targets_active/megafish_target_01_active.png", cv2.IMREAD_UNCHANGED)
img_megafish_target_01_active = cv2.cvtColor(img_megafish_target_01_active, cv2.COLOR_RGB2RGBA)
img_megafish_target_02_active = cv2.imread("img/megafish/targets_active/megafish_target_02_active.png", cv2.IMREAD_UNCHANGED)
img_megafish_target_02_active = cv2.cvtColor(img_megafish_target_02_active, cv2.COLOR_RGB2RGBA)
img_megafish_target_03_active = cv2.imread("img/megafish/targets_active/megafish_target_03_active.png", cv2.IMREAD_UNCHANGED)
img_megafish_target_03_active = cv2.cvtColor(img_megafish_target_03_active, cv2.COLOR_RGB2RGBA)
img_megafish_target_04_active = cv2.imread("img/megafish/targets_active/megafish_target_04_active.png", cv2.IMREAD_UNCHANGED)
img_megafish_target_04_active = cv2.cvtColor(img_megafish_target_04_active, cv2.COLOR_RGB2RGBA)
img_megafish_target_05_active = cv2.imread("img/megafish/targets_active/megafish_target_05_active.png", cv2.IMREAD_UNCHANGED)
img_megafish_target_05_active = cv2.cvtColor(img_megafish_target_05_active, cv2.COLOR_RGB2RGBA)
img_megafish_target_06_active = cv2.imread("img/megafish/targets_active/megafish_target_06_active.png", cv2.IMREAD_UNCHANGED)
img_megafish_target_06_active = cv2.cvtColor(img_megafish_target_06_active, cv2.COLOR_RGB2RGBA)
img_megafish_target_07_active = cv2.imread("img/megafish/targets_active/megafish_target_07_active.png", cv2.IMREAD_UNCHANGED)
img_megafish_target_07_active = cv2.cvtColor(img_megafish_target_07_active, cv2.COLOR_RGB2RGBA)
img_megafish_target_08_active = cv2.imread("img/megafish/targets_active/megafish_target_08_active.png", cv2.IMREAD_UNCHANGED)
img_megafish_target_08_active = cv2.cvtColor(img_megafish_target_08_active, cv2.COLOR_RGB2RGBA)
img_megafish_target_09_active = cv2.imread("img/megafish/targets_active/megafish_target_09_active.png", cv2.IMREAD_UNCHANGED)
img_megafish_target_09_active = cv2.cvtColor(img_megafish_target_09_active, cv2.COLOR_RGB2RGBA)
img_megafish_target_10_active = cv2.imread("img/megafish/targets_active/megafish_target_10_active.png", cv2.IMREAD_UNCHANGED)
img_megafish_target_10_active = cv2.cvtColor(img_megafish_target_10_active, cv2.COLOR_RGB2RGBA)
img_megafish_target_11_active = cv2.imread("img/megafish/targets_active/megafish_target_11_active.png", cv2.IMREAD_UNCHANGED)
img_megafish_target_11_active = cv2.cvtColor(img_megafish_target_11_active, cv2.COLOR_RGB2RGBA)
img_megafish_target_12_active = cv2.imread("img/megafish/targets_active/megafish_target_12_active.png", cv2.IMREAD_UNCHANGED)
img_megafish_target_12_active = cv2.cvtColor(img_megafish_target_12_active, cv2.COLOR_RGB2RGBA)
img_megafish_targets_active = [
                img_megafish_target_01_active,
                img_megafish_target_02_active,
                img_megafish_target_03_active,
                img_megafish_target_04_active,
                img_megafish_target_05_active, 
                img_megafish_target_06_active, 
                img_megafish_target_07_active, 
                img_megafish_target_08_active, 
                img_megafish_target_09_active, 
                img_megafish_target_10_active, 
                img_megafish_target_11_active, 
                img_megafish_target_12_active
            ]

class MegafishBot:
    def __init__(self):
        self.img_targets_active = img_megafish_targets_active
        self.timestamp_last_run = time.perf_counter()
        self.timestamp_last_shiny_catch = time.perf_counter()
        self.time_between_evaluation_seconds = 5
        self.target_1_multiplier = 1
        self.target_2_multiplier = 1
        self.target_3_multiplier = 1
        self.target_4_multiplier = 1
        self.target_5_multiplier = 1
        self.target_6_multiplier = 1
        self.target_7_multiplier = 1
        self.target_8_multiplier = 1
        self.target_9_multiplier = 1
        self.target_10_multiplier = 1
        self.target_11_multiplier = 1
        self.target_12_multiplier = 1
        self.click_counter = 0
        self.grid = Grid3x4()

        self.template_golden_tap = img_megafish_golden_tap
        self.template_golden_tap_w = self.template_golden_tap.shape[1]
        self.template_golden_tap_h = self.template_golden_tap.shape[0]
        self.template_golden_catch = img_megafish_golden_catch
        self.template_golden_catch_w = self.template_golden_catch.shape[1]
        self.template_golden_catch_h = self.template_golden_catch.shape[0]

    def find_golden_catch_pos(self, img_frame):
        template_result = cv2.matchTemplate(img_frame, self.template_golden_catch, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(template_result)
        within_threshold = max_val >= 0.7

        found = False
        max_pos = (0,0)
        if within_threshold:
            found = True
            x = max_loc[0] + self.template_golden_catch_w * 0.5
            y = max_loc[1] + self.template_golden_catch_h * 0.5
            max_pos = (x, y)

        return (found, max_pos)
    
    def find_golden_tap_pos(self, img_frame):
        template_result = cv2.matchTemplate(img_frame, self.template_golden_tap, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(template_result)
        within_threshold = max_val >= 0.7

        found = False
        max_pos = (0,0)
        if within_threshold:
            found = True

            x = max_loc[0] + self.template_golden_tap_w * 0.5
            y = max_loc[1] + self.template_golden_tap_h * 0.5
            max_pos = (x, y)

        return (found, max_pos)

    def click_target(self, target_nr):
        if target_nr == 1:
            print("Not impl")
        elif target_nr == 2:
            print("Not impl")
        elif target_nr == 3:
            print("Not impl")
        elif target_nr == 4:
            print("Not impl")
        elif target_nr == 5:
            print("Not impl")
        elif target_nr == 6:
            print("Not impl")
        elif target_nr == 7:
            print("Not impl")
        elif target_nr == 8:
            print("Not impl")
        elif target_nr == 9:
            print("Not impl")
        
        print("Not impl")

    def debug_draw_thing(self, img_frame, pos_xy, color = (0,255,255)):
        w = 50 
        h = 50
        rect = (int(pos_xy[0] - w*0.5), int(pos_xy[1] - h*0.5), int(w), int(h))
        debug_draw_rectangle(img_frame, rect, color)

    def click_all_12(self, img_frame):
        self.grid.size_xy = (430, 200)
        self.grid.offset_xy = (260, 600)

        for y in range(0,3):
            for x in range(0,4):
                # do not do FISHEROO RESET
                if x >= 3:
                    continue

                mouse_target_xy = self.grid.get_point_position(x+1,y+1)
                self.debug_draw_thing(img_frame, mouse_target_xy)
                if globals.accepting_input:
                    num_fast_clicks = 1
                    for c in range(0,num_fast_clicks):
                        MouseClickPosition(mouse_target_xy)
                        sleep_between_fast_clicks = randFloat(0.01, 0.1)
                        stall(sleep_between_fast_clicks)
                sleep_between_clicks = randFloat(0.25, 0.5)
                stall(sleep_between_clicks)
            

    def find_active_targets(self, img_frame):
        targets_active_list = []
        for i in range(0, self.img_targets_active.__len__()):
            match_result = cv2.matchTemplate(img_frame, self.img_targets_active[i], cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(match_result)
            match_threshold = 0.5
            if max_val >= match_threshold:
                rect = (max_loc[0], max_loc[1], self.img_targets_active[i].shape[1], self.img_targets_active[i].shape[0])
                targets_active_list.append((i, rect))

        return targets_active_list
    
    def click_bot(self, img_frame):
        # todo, find active targets
        # then decide what to click, in what order,

        active_targets = self.find_active_targets(img_frame)

        avoid_clicking_targets = [7, 10, 12]
        for i in range(0, active_targets.__len__()):
            (x,y,w,h) = active_targets[i][1]
            mouse_target_xy = (x + int(0.5 * w), y + int(0.5 * h))
            
            #skip avoid targets
            if active_targets[i][0] + 1 == avoid_clicking_targets[0]:
                self.debug_draw_thing(img_frame, mouse_target_xy, (255, 0, 0))
                continue
            if active_targets[i][0] + 1 == avoid_clicking_targets[1]:
                self.debug_draw_thing(img_frame, mouse_target_xy, (255, 0, 0))
                continue
            if active_targets[i][0] + 1 == avoid_clicking_targets[2]:
                self.debug_draw_thing(img_frame, mouse_target_xy, (255, 0, 0))
                continue

            self.debug_draw_thing(img_frame, mouse_target_xy)
            if globals.accepting_input:
                num_fast_clicks = 10
                for c in range(0,num_fast_clicks):
                    MouseClickPosition(mouse_target_xy)
                    sleep_between_fast_clicks = randFloat(0.01, 0.1)
                    # stall(sleep_between_fast_clicks)
                    time.sleep(sleep_between_fast_clicks)
            sleep_between_clicks = randFloat(0.1, 0.5)
            # stall(sleep_between_clicks)
            time.sleep(sleep_between_clicks)
        

    def do_mouse_clicks(self, img_frame):
        # mouse_target_xy = (1, 1)
        # MouseClickPosition(mouse_target_xy)
        # self.click_all_12(img_frame)
        self.click_bot(img_frame)



    def do_shiny_catch(self, img_frame, current_time):
        (found_golden_catch, golden_catch_pos) = self.find_golden_catch_pos(img_frame)
        if found_golden_catch:
            print("clicking golden_catch, then stalling for 1s")
            if globals.accepting_input:
                MouseClickPosition(golden_catch_pos)
            stall(1)
            self.timestamp_last_shiny_catch = current_time

            w = 50 
            h = 50
            rect = (int(golden_catch_pos[0] - w*0.5), int(golden_catch_pos[1] - h*0.5), int(w), int(h))
            debug_draw_rectangle(img_frame, rect, color=(200, 255, 0))

        (found_golden_tap, golden_catch_tap) = self.find_golden_tap_pos(img_frame)
        if found_golden_tap:
            print("clicking golden_tap, then stalling for 1s")
            if globals.accepting_input:
                MouseClickPosition(golden_catch_tap)
            stall(0.1)

            w = 50 
            h = 50
            rect = (int(golden_catch_tap[0] - w*0.5), int(golden_catch_tap[1] - h*0.5), int(w), int(h))
            debug_draw_rectangle(img_frame, rect, color=(200, 150, 0))
    
    def try_shiny_catch(self, img_frame, current_time):
        shiny_catch_timeout_seconds = 20
        elapsed_since_last_shiny_catch = current_time - self.timestamp_last_shiny_catch
        allowed_shiny_catch = elapsed_since_last_shiny_catch >= shiny_catch_timeout_seconds
        if allowed_shiny_catch:
            self.do_shiny_catch(img_frame, current_time)
            return True
        
        return False

    def run(self, img_frame):
        current_time = time.perf_counter()

        elapsed_since_last_run = current_time - self.timestamp_last_run

        if elapsed_since_last_run >= self.time_between_evaluation_seconds:
            self.try_shiny_catch(img_frame, current_time)

            print("DOING CLICKS")
            self.do_mouse_clicks(img_frame)

            self.timestamp_last_run = current_time

        

