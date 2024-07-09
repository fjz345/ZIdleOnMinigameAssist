from decimal import Decimal
import math
import time
import cv2
from misc import *
from debug_draw import *

img_chopping_marker = cv2.imread("img/chopping/chopping_marker_super_trimmed_alpha.png", cv2.IMREAD_UNCHANGED)
img_chopping_marker = cv2.cvtColor(img_chopping_marker, cv2.COLOR_RGB2RGBA)

img_chopping_bar = cv2.imread("img/chopping/chopping_bar_alpha.png", cv2.IMREAD_UNCHANGED)
img_chopping_bar = cv2.cvtColor(img_chopping_bar, cv2.COLOR_RGB2RGBA)

choppingbot_state_init = 0
choppingbot_state_doing_inputs = 1
choppingbot_state_game_over = 2

class PixelStepper:
    def __init__(self):
        self.index = 0
        self.img = []

    def open(self, img):
        if img.shape[0] <= 0:
            print("img y <= 0")
        if img.shape[1] <= 0:
            print("img x <= 0")
        if img.shape[0] > 1:
            print("img y not 1, only row 1 will get read")
        self.reset()
        self.img = img

    def reset(self):
        self.index = 0

    def get_index(self):
        return self.index
    
    def is_at_end(self):
        return self.index >= self.img.shape[1]-1

    def next_g_greater_than(self, g_treshold):
        found_next_g = False
        found_next_g_index = -1
        found_next_g_val = -1

        x_start = self.index
        for i in range(x_start, self.img.shape[1]-1):
            (r,g,b,a) = self.img[0][i]

            if g >= g_treshold:
                found_next_g = True
                found_next_g_val = g
                found_next_g_index = i
                break
        
        #update index
        if found_next_g:
            self.index = min(found_next_g_index + 1,self.img.shape[1]-1)
        else:
            self.index = self.img.shape[1]-1

        return (found_next_g, found_next_g_index, found_next_g_val)
    
    def next_g_greater_than_inverse(self, g_treshold):
        found_next_g = False
        found_next_g_index = -1
        found_next_g_val = -1

        x_start = self.index
        for i in range(x_start, self.img.shape[1]-1):
            (r,g,b,a) = self.img[0][i]

            if g < g_treshold:
                found_next_g = True
                found_next_g_val = g
                found_next_g_index = i
                break
        
        #update index
        if found_next_g:
            self.index = min(found_next_g_index + 1,self.img.shape[1]-1)
        else:
            self.index = self.img.shape[1]-1

        return (found_next_g, found_next_g_index, found_next_g_val)
    
class ChoppingBot:
    def __init__(self):
        self.img_bar = img_chopping_bar
        self.img_bar_w = self.img_bar.shape[1]
        self.img_bar_h = self.img_bar.shape[0]

        self.img_marker = img_chopping_marker
        self.img_marker_w = self.img_marker.shape[1]
        self.img_marker_h = self.img_marker.shape[0]

        self.state = choppingbot_state_init
        self.idle_state_enter_timestamp = -1.0
        self.doing_inputs_state_enter_timestamp = -1.0
        self.clicks_done = 0
        self.click_margin_px = 50
        self.curr_margin_px = 0

        self.side_bounces = 0
        self.bounce_fence = 0
        self.clicks_done_this_iteration = 0

        #marker
        self.marker_found_this_frame = False
        self.marker_rect_curr_frame = (0,0,0,0)
        self.marker_pos_curr_frame = -1.0
        self.marker_pos_last_frame = -1.0
        self.marker_pos_min = -1.0
        self.marker_pos_max = -1.0
        self.marker_curr_vel = -1.0
        self.marker_last_vel = -1.0

        #bar
        self.bar_found = False
        self.bar_rect = (0,0,0,0)
        self.bar_pixel_data = []
        self.bar_red_rect = (0,0,0,0)
        self.good_ranges = []

        #bar colors (RGB)
        self.red_dark = (115, 7, 44)
        self.red_light = (216, 81, 97)
        self.green_dark = (45, 155, 23)
        self.green_light = (126, 223, 42)
        self.yellow_dark = (224, 169, 46)
        self.yellow_light = (248, 255, 127)
        # G >= 100 is safe

        self.stepper = PixelStepper()

    def ready_for_input(self):
        is_ready = self.bar_found and           \
                    self.marker_pos_min != -1.0 and \
                    self.marker_pos_max != -1.0
        
        return is_ready

    # Do more clicks in the beginning
    # in [0,inf]
    def clicks_to_do(self, duration_elapsed):
        x = duration_elapsed
        a = -0.06
        b = 5.0
        y = b*math.exp(a*x)

        y += 1
        y = max(y, 1)
        return int(y)


    def find_marker(self, img_frame):
        marker_result = cv2.matchTemplate(img_frame, self.img_marker, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(marker_result)
        marker_threshold = 0.4
        rect = (0,0,0,0)
        within_threshold = max_val >= marker_threshold
        if within_threshold:
            rect = (max_loc[0], max_loc[1], self.img_marker_w, self.img_marker_h)

        return (within_threshold, rect)
    
    def find_bar(self, img_frame):
        result = cv2.matchTemplate(img_frame, self.img_bar, cv2.TM_CCORR_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        bar_threshold = 0.2
        rect = (0,0,0,0)
        within_threshold = max_val >= bar_threshold
        if within_threshold:
            rect = (max_loc[0], max_loc[1], self.img_bar_w, self.img_bar_h)

        return (within_threshold, rect)

    def collect_marker_data(self, img_frame, dt):
        self.marker_pos_last_frame = self.marker_pos_curr_frame

        self.marker_found_this_frame = False
        (found_marker, marker_rect) = self.find_marker(img_frame)
        if found_marker:
            self.marker_found_this_frame = True
            self.marker_rect_curr_frame = marker_rect
            self.marker_pos_curr_frame = marker_rect[0]

            if self.marker_pos_min == -1.0:
                self.marker_pos_min = self.marker_pos_curr_frame
            if self.marker_pos_max == -1.0:
                self.marker_pos_max = self.marker_pos_curr_frame

            self.marker_pos_min = min(self.marker_pos_min, self.marker_pos_curr_frame)
            self.marker_pos_max = max(self.marker_pos_max, self.marker_pos_curr_frame)

            # Update velocity
            if self.marker_pos_curr_frame != -1.0 and self.marker_pos_last_frame != -1.0:
                self.marker_curr_vel = dt*(self.marker_pos_curr_frame - self.marker_pos_last_frame)
                if np.sign(self.marker_last_vel) != np.sign(self.marker_curr_vel):
                    self.side_bounces += 1
            self.marker_last_vel = self.marker_curr_vel
        
            
    def init_bar_data(self, img_frame, dt):
        (found_bar, rect) = self.find_bar(img_frame)
        if found_bar:
            self.bar_found = True
            self.bar_rect = rect

            self.bar_min = self.bar_rect[0]
            self.bar_max = self.bar_rect[0] + self.bar_rect[2]

    def collect_bar_data(self, img_frame, dt):
        (x,y,w,h) = self.bar_rect
        # measured data calculation for red bar part
        y_manual_offset = 0
        #25, 51
        #578, 64
        bar_red_measured_rect_min = (25, y_manual_offset + 51)
        bar_red_measured_rect_max = (578, y_manual_offset + 64)
        bar_red_min = (x + bar_red_measured_rect_min[0], y + bar_red_measured_rect_min[1])
        bar_red_max = (x + bar_red_measured_rect_max[0], y + bar_red_measured_rect_max[1])
        bar_red_w = bar_red_max[0] - bar_red_min[0]
        bar_red_h = bar_red_max[1] - bar_red_min[1]
        self.bar_red_rect = (bar_red_min[0], bar_red_min[1], bar_red_w, bar_red_h)

        clip_min = bar_red_min
        clip_max = bar_red_max
        img_clipped = img_frame[clip_min[1]:clip_max[1], clip_min[0]:clip_max[0]]

        center_y = int((clip_max[1] - clip_min[1]) / 2)
        self.bar_pixel_data = img_clipped[center_y:(center_y+1), clip_min[0]:clip_max[0]]

        self.good_ranges = self.find_good_ranges(self.bar_pixel_data)

    # returns the biggest target range
    def find_good_ranges(self, bar_pixel_data):
        found_ranges = []
        
        g_threshold = 100
        self.stepper.open(bar_pixel_data)

        (found_first_valid_g, first_valid_g_index, first_valid_g_val) = self.stepper.next_g_greater_than(g_threshold)
        if found_first_valid_g:
            last_g_index = first_valid_g_index
            searching_for_green = False
            while(not self.stepper.is_at_end()):
                if searching_for_green:
                    (f, i, v) = self.stepper.next_g_greater_than(g_threshold)
                    if f:
                        last_g_index = i
                    else:
                        break
                else:
                    (f, i, v) = self.stepper.next_g_greater_than_inverse(g_threshold)
                    if i == -1:
                        i = self.stepper.get_index()
                    found_ranges.append((last_g_index, i))

                searching_for_green = not searching_for_green
        # print("Found ranges:")
        # print(found_ranges)
        return found_ranges

   #returns (index, size)
    def find_best_range(self, ranges):
        found_index = -1
        found_size = -1

        for i in range(0, ranges.__len__()):
            min = ranges[i][0]
            max = ranges[i][1]
            size = max - min
            if size > found_size:
                found_size = size
                found_index = i
        return (found_index, found_size)

    def should_click(self, marker_rect, bar_red_rect, marker_vel, good_click_ranges):
        (best_range_index, best_range_size) = self.find_best_range(good_click_ranges)
        if best_range_index == -1:
            print("Best range not found")
            print(good_click_ranges)
            return False
        min_ok_size = 10
        if best_range_size < min_ok_size:
            print("Best range size < min_ok_size")
            return False

        best_range = good_click_ranges[best_range_index]

        marker_center_x = marker_rect[0] + marker_rect[2] / 2

        x = marker_center_x - bar_red_rect[0]
        
        vel_dir = np.sign(marker_vel)
        self.curr_margin_px = vel_dir*self.click_margin_px
        x_with_margin = x + self.curr_margin_px
        should_click = is_val_within_range(x, best_range) and is_val_within_range(x_with_margin, best_range)
        
        return should_click

    def do_clicks(self):
        if globals.accepting_input:
            SpaceDown()
            stall(0.001)
            SpaceUp()
        print("CLICKED %d" % (1))
        self.clicks_done += 1

    def run(self, img_frame, dt):
        current_time = time.perf_counter()
        if self.state == choppingbot_state_init:

            if self.idle_state_enter_timestamp == -1.0:
                self.idle_state_enter_timestamp = current_time

            self.init_bar_data(img_frame, dt)
            self.collect_marker_data(img_frame, dt)

            elapsed_since_idle_state_enter = current_time - self.idle_state_enter_timestamp
            duration_state_sec = 1
            if elapsed_since_idle_state_enter >= duration_state_sec:
                self.state = choppingbot_state_doing_inputs
                doing_inputs_state_enter_timestamp = current_time
                self.clicks_done = 0
                print("Chopping init done, starting doing clicks")

        elif self.state == choppingbot_state_doing_inputs:
            # globals.performance_critical = True
            self.collect_marker_data(img_frame, dt)
            self.collect_bar_data(img_frame, dt)

            new_bounce = self.bounce_fence != self.side_bounces
            if new_bounce:
                print("New Bounce...")
                self.clicks_done_this_iteration = 0
                self.bounce_fence = self.side_bounces

            if self.marker_found_this_frame:
                elapsed = current_time - self.doing_inputs_state_enter_timestamp
                num_clicks = self.clicks_to_do(elapsed)
                can_do_num_clicks_this_iteration = num_clicks - self.clicks_done_this_iteration
                can_click_this_iteration = can_do_num_clicks_this_iteration > 0
                if can_click_this_iteration:
                    should_click = self.should_click(self.marker_rect_curr_frame, self.bar_red_rect, self.marker_curr_vel, self.good_ranges)
                    # DEBUG should_click THIS HERE VISUALLY Green/Red
                    # MAYBE ADD, constnat padding inside should click
                    if should_click:
                        print("Clicks left: %d" % can_do_num_clicks_this_iteration)
                        self.do_clicks()
                        self.clicks_done_this_iteration += 1

            # check if game over

        elif self.state == choppingbot_state_game_over:
            globals.performance_critical = False
            print("Chopping game over: %d clicks" % (self.clicks_done))



        if not globals.performance_critical:
            self.debug_draw(img_frame)

    def debug_draw_marker(self, img_frame):
        if self.img_marker_w != 0 and self.img_marker_h != 0:
            if self.marker_found_this_frame:
                (x,y,w,h) = self.marker_rect_curr_frame
                margin_rect = (x + self.curr_margin_px, y, w, h)

                debug_draw_rectangle(img_frame, self.marker_rect_curr_frame)
                debug_draw_rectangle(img_frame, margin_rect, (255, 0, 0))

                y = self.marker_rect_curr_frame[1]
                debug_draw_circle(img_frame, (self.marker_pos_min, y), 5, (255, 0, 0))
                debug_draw_circle(img_frame, (self.marker_pos_max, y), 5, (0, 0, 255))

    def debug_draw_bar(self, img_frame):
        if self.bar_found:
            debug_draw_rectangle(img_frame, self.bar_rect)
            debug_draw_rectangle(img_frame, self.bar_red_rect)


    def debug_draw(self, img_frame):
        self.debug_draw_marker(img_frame)
        self.debug_draw_bar(img_frame)
        

    def get_last_match(self):
        return (self.last_result, self.last_locs_x, self.last_locs_y)        