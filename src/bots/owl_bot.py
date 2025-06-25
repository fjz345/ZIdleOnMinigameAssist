from decimal import Decimal
import math
import time
import cv2
from misc import *
import globals
from debug_draw import *

class Grid9:
    def __init__(self):
        self.grid_points = [(0,0),(1,0),(2,0),
                            (0,1),(1,1),(2,1),
                            (0,2),(1,2),(2,2)]
        
        self.size_xy = (1,1)
        self.offset_xy = (20,10)

    def get_point_position(self, nr1to9):
        x = self.offset_xy[0] + self.size_xy[0] * self.grid_points[nr1to9-1][0]
        y = self.offset_xy[1] + self.size_xy[1] * self.grid_points[nr1to9-1][1]
        return (x,y)

class OwlBot:
    def __init__(self, img_targets_1to9_list):
        self.img_targets_1to9_list = img_targets_1to9_list
        self.timestamp_last_run = time.perf_counter()
        self.time_between_evaluation_seconds = 1
        self.target_1_multiplier = 1
        self.target_2_multiplier = 10000
        self.target_3_multiplier = 1
        self.target_4_multiplier = 1
        self.target_5_multiplier = 100
        self.target_6_multiplier = 5
        self.target_7_multiplier = 10
        self.target_8_multiplier = 2
        self.target_9_multiplier = 1000
        self.click_counter = 0
        self.grid = Grid9()

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

    def debug_draw_thing(self, img_frame, pos_xy):
        w = 50
        h = 50
        rect = (int(pos_xy[0] - w*0.5), int(pos_xy[1] - h*0.5), int(w), int(h))
        debug_draw_rectangle(img_frame, rect)

    def click_all_9(self, img_frame):
        self.grid.size_xy = (480, 290)
        self.grid.offset_xy = (280, 150)

        for i in range(0, 9):
            mouse_target_xy = self.grid.get_point_position(i)
            self.debug_draw_thing(img_frame, mouse_target_xy)
            if globals.accepting_input:
                num_fast_clicks = 10
                for c in range(0,num_fast_clicks):
                    MouseClickPosition(mouse_target_xy)
                    sleep_between_fast_clicks = randFloat(0.01, 0.1)
                    stall(sleep_between_fast_clicks)
            sleep_between_clicks = randFloat(0.25, 0.5)
            stall(sleep_between_clicks)
        

    def do_mouse_clicks(self, img_frame):
        # mouse_target_xy = (1, 1)
        # MouseClickPosition(mouse_target_xy)
        self.click_all_9(img_frame)
    
    def run(self, img_frame):
        current_time = time.perf_counter()

        elapsed_since_last_run = current_time - self.timestamp_last_run

        if elapsed_since_last_run >= self.time_between_evaluation_seconds:
            print("DOING CLICKS")
            self.do_mouse_clicks(img_frame)

            self.timestamp_last_run = current_time

        

