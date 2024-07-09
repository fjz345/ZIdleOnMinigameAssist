from decimal import Decimal
import math
import time
import cv2
from misc import *
import globals
from debug_draw import *

class FishingDecidedInput:
    def __init__(self):
        self.isDecided = False
        self.hold_duration_ms = -1.0
        self.power = -1.0
        self.t = -1.0
        self.timestamp_decided = -1.0
        self.timestamp_start_holding = -1.0
        self.timestamp_stop_holding = -1.0

# linear state machine
fishing_state_init = 0
fishing_state_idle = 1
fishing_state_choose_target = 2
fishing_state_collect_target_t = 3
fishing_state_do_input = 4
fishing_state_wait_for_new_round = 5
class FishingState:
    def __init__(self):
        self.reset()
        # Should increase each spacebar input
        self.level_count = 0
        self.whale_count = 0
        self.whale_third_missed = False
        self.megalodon_count = 0

    def reset(self):
        self.state = fishing_state_idle
        # 0 is none
        self.selected_target = 0
        # when targets move, store min/max t
        self.selected_target_left_t = 0.0
        self.selected_target_right_t = 0.0
        self.selected_target_left_t_timestamp = 0
        self.selected_target_right_t_timestamp = 0
        self.closest_distance_to_mine = -1.0
        self.timestamp_collect_target_t = -1.0
        self.timestamp_selected_target = -1.0
        self.timestamp_do_input = -1.0
        self.timestamp_wait_new_round = -1.0
        self.decided_input = FishingDecidedInput()

img_fishing_bar = cv2.imread("img/fishing/fish_bar.png", cv2.IMREAD_UNCHANGED)
img_fishing_bar = cv2.cvtColor(img_fishing_bar, cv2.COLOR_RGB2RGBA)
img_fishing_waterrange = cv2.imread("img/fishing/fish_waterrange_alpha.png", cv2.IMREAD_UNCHANGED)
img_fishing_mine = cv2.imread("img/fishing/fish_mine_edited.png", cv2.IMREAD_UNCHANGED)
img_fishing_mine = cv2.cvtColor(img_fishing_mine, cv2.COLOR_RGB2RGBA)
img_fishing_target_1 = cv2.imread("img/fishing/fish_target_1.png", cv2.IMREAD_UNCHANGED)
img_fishing_target_1 = cv2.cvtColor(img_fishing_target_1, cv2.COLOR_RGB2RGBA)
img_fishing_target_2 = cv2.imread("img/fishing/fish_target_2_noalpha.png", cv2.IMREAD_UNCHANGED)
img_fishing_target_2 = cv2.cvtColor(img_fishing_target_2, cv2.COLOR_RGB2RGBA)
img_fishing_target_3 = cv2.imread("img/fishing/fish_target_3_alpha.png", cv2.IMREAD_UNCHANGED)
img_fishing_target_3 = cv2.cvtColor(img_fishing_target_3, cv2.COLOR_RGB2RGBA)
img_fishing_target_4 = cv2.imread("img/fishing/fish_target_4_alpha.png", cv2.IMREAD_UNCHANGED)
img_fishing_target_4 = cv2.cvtColor(img_fishing_target_4, cv2.COLOR_RGB2RGBA)
img_fishing_target_5 = cv2.imread("img/fishing/fish_target_5_alpha.png", cv2.IMREAD_UNCHANGED)
img_fishing_target_5 = cv2.cvtColor(img_fishing_target_5, cv2.COLOR_RGB2RGBA)
img_fishing_targets = [
                        img_fishing_target_1, 
                        img_fishing_target_2, 
                        img_fishing_target_3, 
                        img_fishing_target_4,
                        img_fishing_target_5,
                       ]
img_fishing_test = cv2.imread("img/fishing/fish_full.png", cv2.IMREAD_UNCHANGED)

class FishingBot:
    def __init__(self):
        self.img_bar = img_fishing_bar
        self.bar_w = img_fishing_bar.shape[1]
        self.bar_h = img_fishing_bar.shape[0]
        self.img_waterrange = img_fishing_waterrange
        self.waterrange_w = img_fishing_waterrange.shape[1]
        self.waterrange_h = img_fishing_waterrange.shape[0]
        self.img_avoidtarget = img_fishing_mine
        self.avoidtarget_w = img_fishing_mine.shape[1]
        self.avoidtarget_h = img_fishing_mine.shape[0]
        self.img_target1 = img_fishing_target_1
        self.target1_w = img_fishing_target_1.shape[1]
        self.target1_h = img_fishing_target_1.shape[0]
        self.img_target2 = img_fishing_target_2
        self.target2_w = img_fishing_target_2.shape[1]
        self.target2_h = img_fishing_target_2.shape[0]
        self.img_target3 = img_fishing_target_3
        self.target3_w = img_fishing_target_3.shape[1]
        self.target3_h = img_fishing_target_3.shape[0]
        self.img_target4 = img_fishing_target_4
        self.target4_w = img_fishing_target_4.shape[1]
        self.target4_h = img_fishing_target_4.shape[0]
        self.img_target5 = img_fishing_target_5
        self.target5_w = img_fishing_target_5.shape[1]
        self.target5_h = img_fishing_target_5.shape[0]

        self.waterrange_rect = (0,0,0,0)
        self.bar_rect = (0,0,0,0)
        self.avoidtarget_rects = []
        self.avoidtarget_rect = (0,0,0,0)
        self.target1_rect = (0,0,0,0)
        self.target2_rect = (0,0,0,0)
        self.target3_rect = (0,0,0,0)
        self.target4_rect = (0,0,0,0)
        self.target5_rect = (0,0,0,0)

        self.target_exists_threshold = 0.98
        self.target_4_exists_threshold = 0.97
        self.target_5_exists_threshold = 0.97

        # 124 / 824
        self.dist_unreachable_left = self.waterrange_w * 0.1505
        # 57 / 824
        self.dist_unreachable_right = self.waterrange_w * 0.0692
        self.total_reachable_dist = self.waterrange_w - self.dist_unreachable_left - self.dist_unreachable_right
        
        self.color_waterrange = (0, 100, 0)
        self.color_avoidtarget = (0, 0, 255)
        self.color_target1 = (0, 240, 0)
        self.color_target2 = (0, 200, 255)
        self.color_target3 = (255, 255, 200)
        self.color_target4 = (89, 169, 255)

        self.color_valuescale = 0.2

        self.fishing_state = FishingState()
        self.manual_power = -1

    def find_waterrange_rect(self, img_frame):
        result = cv2.matchTemplate(img_frame, self.img_waterrange, cv2.TM_CCOEFF_NORMED, None, self.img_waterrange)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        waterrange_threshold = 0.6
        rect = (0,0,0,0)
        if max_val >= waterrange_threshold:
            rect = (max_loc[0], max_loc[1], self.waterrange_w, self.waterrange_h)
            return (True, rect)
        return (False, rect)

    def find_bar_rect(self, img_frame):
        result = cv2.matchTemplate(img_frame, self.img_bar, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        bar_threshold = 0.8
        rect = (0,0,0,0)
        if max_val >= bar_threshold:
            rect = (max_loc[0], max_loc[1], self.bar_w, self.bar_h)
            return (True, rect)
        return (False, rect)

    def find_avoidtargets(self, img_frame):
        result = cv2.matchTemplate(img_frame, self.img_avoidtarget, cv2.TM_CCORR_NORMED, None, self.img_avoidtarget)
        (locs_x, locs_y) = filter_locs(result, 0.98)

        avoidtarget_rects = gather_match_results(self.avoidtarget_w, self.avoidtarget_h, locs_x, locs_y, 0.2)
        found = avoidtarget_rects.__len__() > 0
        return (found, avoidtarget_rects)

    def find_target(self, img_frame, index):
        if index == 1:
            return self.find_target_1(img_frame)
        if index == 2:
            return self.find_target_2(img_frame)
        if index == 3:
            return self.find_target_3(img_frame)
        if index == 4:
            return self.find_target_4(img_frame)
        if index == 5:
            return self.find_target_5(img_frame)

    def find_target_1(self, img_frame):
        result = cv2.matchTemplate(img_frame, self.img_target1, cv2.TM_CCORR_NORMED, None, self.img_target1)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        target_rect = (max_loc[0], max_loc[1], self.target1_w, self.target1_h)
        within_threshold = max_val >= self.target_exists_threshold
        return (within_threshold, target_rect)
    
    def find_target_2(self, img_frame):
        result = cv2.matchTemplate(img_frame, self.img_target2, cv2.TM_CCORR_NORMED, None, self.img_target2)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        target_rect = (max_loc[0], max_loc[1], self.target2_w, self.target2_h)
        within_threshold = max_val >= self.target_exists_threshold
        return (within_threshold, target_rect)
    
    def find_target_3(self, img_frame):
        result = cv2.matchTemplate(img_frame, self.img_target3, cv2.TM_CCORR_NORMED, None, self.img_target3)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        target_rect = (max_loc[0], max_loc[1], self.target3_w, self.target3_h)
        within_threshold = max_val >= self.target_exists_threshold
        return (within_threshold, target_rect)
    
    def find_target_4(self, img_frame):
        result = cv2.matchTemplate(img_frame, self.img_target4, cv2.TM_CCORR_NORMED, None, self.img_target4)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        target_rect = (max_loc[0], max_loc[1], self.target4_w, self.target4_h)
        within_threshold = max_val >= self.target_4_exists_threshold
        return (within_threshold, target_rect)
    
    def find_target_5(self, img_frame):
        result = cv2.matchTemplate(img_frame, self.img_target5, cv2.TM_CCORR_NORMED, None, self.img_target5)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        target_rect = (max_loc[0], max_loc[1], self.target5_w, self.target5_h)
        within_threshold = max_val >= self.target_5_exists_threshold
        return (within_threshold, target_rect)

    def update_avoidtarget_rects(self, img_frame):
        (found, avoidtarget_rects) = self.find_avoidtargets(img_frame)
        if found:
            self.avoidtarget_rects = avoidtarget_rects
        return found
    
    def update_target(self, img_frame, index):
        if index == 1:
            self.update_target1_rect(img_frame)
        elif index == 2:
            self.update_target2_rect(img_frame)
        elif index == 3:
            self.update_target3_rect(img_frame)
        elif index == 4:
            self.update_target4_rect(img_frame)
        elif index == 5:
            self.update_target5_rect(img_frame)

    def update_target1_rect(self, img_frame):
        (found, target_rect) = self.find_target_1(img_frame)
        if found:
            self.target1_rect = target_rect
        return found

    def update_target2_rect(self, img_frame):
        (found, target_rect) = self.find_target_2(img_frame)
        if found:
            self.target2_rect = target_rect
        return found


    def update_target3_rect(self, img_frame):
        (found, target_rect) = self.find_target_3(img_frame)
        if found:
            self.target3_rect = target_rect
        return found

    def update_target4_rect(self, img_frame):
        (found, target_rect) = self.find_target_4(img_frame)
        if found:
            self.target4_rect = target_rect
        return found
    
    def update_target5_rect(self, img_frame):
        (found, target_rect) = self.find_target_5(img_frame)
        if found:
            self.target5_rect = target_rect
        return found

    def get_dist_2_target_rect(self, target_rect):
        target = rect_center(target_rect)
        t = self.find_target_t(target_rect)
        rect = (int(target[0] - (target[0] - self.waterrange_rect[0]) + self.dist_unreachable_left),
                      int(self.waterrange_rect[1]),
                        int(t * self.total_reachable_dist),
                          int(self.waterrange_rect[3]))
        return rect
    
    def draw_all_t(self, img_frame):
        t_to_draw = []

        for i in range(1,5):
            (found, rect) = self.find_target(img_frame, i)
            if found:
                t = self.find_target_t(rect)
                t_to_draw.append((t, rect[0] + rect[2] ))

        x_nudge = -50
        y_nudge = 30
        pos_y = self.waterrange_rect[1] + self.waterrange_rect[3]
        pos_y += y_nudge
        pos_y = int(pos_y)
        sub_string_len = 3
        for (t, pos_x) in t_to_draw:
            debug_draw_text(img_frame,
                    str(t)[0:sub_string_len+1],
                    (pos_x+x_nudge, pos_y))
            power = self.calc_power_from_t(t)
            debug_draw_text(img_frame,
                    str(power)[0:sub_string_len+1],
                    (pos_x+x_nudge, pos_y + 30))

    # "target_rect" space
    def closest_rect_distance_to_mine(self, rect):
        in_x = rect_center(rect)[0]

        closest_dist = 99999999.0
        for i in range(0,self.avoidtarget_rects.__len__()):
            avoid_target_x = rect_center(self.avoidtarget_rects[i])[0]
            distance = abs(in_x - avoid_target_x)
            closest_dist = min(closest_dist, distance)

        return closest_dist

    #returns [1,4], best target, trying to avoid mines        
    def find_catch_target(self, img_frame):
        if globals.catching_megalodon:
            (found_megalodon, rect_megalodon) = self.find_target_5(img_frame)
            if found_megalodon:
                rect = rect_megalodon
                return (5, rect)
            
            if self.fishing_state.whale_count <= 1:
                # Need to catch whale
                (found_whale, rect_whale) = self.find_target_4(img_frame)
                if found_whale:
                    rect = rect_whale
                    return (4, rect)
                (found, rect_fish) = self.find_target_1(img_frame)
                if found:
                    rect = rect_fish
                    return (1, rect)
            elif self.fishing_state.whale_count >= 2 and not self.fishing_state.whale_third_missed:
                # Miss the whale
                (found, rect_fish) = self.find_target_1(img_frame)
                if found:
                    rect = rect_fish
                    return (1, rect)
            elif self.fishing_state.whale_count >= 2 and self.fishing_state.whale_third_missed:
                # Catch until megelodon appears
                (found, rect_fish) = self.find_target_1(img_frame)
                if found:
                    rect = rect_fish
                    return (1, rect)

        else:
            # Target 1 is never occluded, best success chance for bot
            (found, rect_fish) = self.find_target_1(img_frame)
            if found:
                rect = rect_fish
                return (1, rect)

        return 0
    
    def debug_draw_level_counters(self, img_frame):
        debug_draw_text(img_frame,
            "L: " + str(self.fishing_state.level_count),
            (40,100))
        debug_draw_text(img_frame,
            "W ("+str(int(self.fishing_state.whale_third_missed))+"): " + str(self.fishing_state.whale_count),
            (40,145))
        debug_draw_text(img_frame,
            "M: " + str(self.fishing_state.megalodon_count),
            (40,185))

    def debug_draw_t_info(self, img_frame):
        sub_string_len = 4
        start_pos_x = 400
        start_pos_y = 25
        debug_draw_text(img_frame,
                    "t_left: " + str(self.fishing_state.selected_target_left_t)[0:sub_string_len],
                    (start_pos_x, start_pos_y))
        debug_draw_text(img_frame,
                    "t_right: " + str(self.fishing_state.selected_target_right_t)[0:sub_string_len],
                    (start_pos_x, start_pos_y + 40))
        # debug_draw_text(img_frame,
        #             "t_time: " + str(self.fishing_state.selected_target_time_between_ts)[0:sub_string_len],
        #             (start_pos_x, start_pos_y + 80))

    def debug_draw_manual_power(self, img_frame):
        debug_draw_text(img_frame,
                    "Manual: " + str(self.manual_power)[0:3],
                    (400, 100))

    def draw_info(self, img_frame):
        self.debug_draw_t_info(img_frame)

        powers_to_draw = []
        pos_counter = 0
        pos_counter_inc = 40
        for i in range(1,5):
            (found, rect) = self.find_target(img_frame, i)
            if found:
                t = t = self.find_target_t(rect)
                power = self.calc_power_from_t(t)
                powers_to_draw.append((power, pos_counter ))
                pos_counter += pos_counter_inc

        sub_string_len = 3
        start_pos_x = 200
        start_pos_y = 25
        for (power, pos) in powers_to_draw:
            debug_draw_text(img_frame,
                    "P: " + str(power)[0:sub_string_len],
                    (start_pos_x, start_pos_y + pos))
            
        self.debug_draw_manual_power(img_frame)

    def get_target_rect_index(self, index):
        if index == 1:
            return self.target1_rect
        if index == 2:
            return self.target2_rect
        if index == 3:
            return self.target3_rect
        if index == 4:
            return self.target4_rect
        if index == 5:
            return self.target5_rect
        
    def get_target_color_index(self, index):
        if index == 1:
            return self.color_target1
        if index == 2:
            return self.color_target2
        if index == 3:
            return self.color_target3
        if index == 4:
            return self.color_target4
        

    def debug_draw_dist_rects(self, img_frame):
        rects_to_draw = []

        for i in range(1,5):
            (found, rect) = self.find_target(img_frame, i)
            if found:
                debug_target_rect = self.get_dist_2_target_rect(rect)
                debug_target_color = self.get_target_color_index(i)
                rects_to_draw.append((debug_target_rect, debug_target_color))
        
        rects_to_draw.sort(key=lambda x:(x[0][2]), reverse=True)

        for (rect, color) in rects_to_draw:
            debug_draw_rectangle(img_frame, rect, color)

    def debug_draw_targets(self, img_frame):
        for i in range(1,5):
            (found, rect) = self.find_target(img_frame, i)
            if found:
                debug_target_rect = rect
                debug_target_color = self.get_target_color_index(i)
                debug_draw_rectangle(img_frame, debug_target_rect, debug_target_color)

    def debug_draw(self, img_frame):
        debug_draw_rects(img_frame, self.avoidtarget_rects, self.color_avoidtarget)
        
        debug_draw_text(img_frame,
                    "State: " + str(self.fishing_state.state),
                    (40, 25))
        
        self.draw_info(img_frame)

        self.debug_draw_level_counters(img_frame)
    
    # Power [0,7]
    def calc_power_bar_mod_factor_cubic(self, power):
        '''
        Power_bar - frames
        0 - 0
        0->0.5 - 9 (9)
        0.5->1 - 14 (23)
        1->1.5 - 5 (28)
        1.5->2 - 4 (32)
        2->2.5 - 3 (35)
        2.5->3 - 3 (38)
        3->3.5 - 3 (41)
        3.5->4 - 3 (44)
        4->4.5 - 2 (46)
        4.5->5 - 3 (49)
        5.5->6 - 2 (51)
        6->6.5 - 3 (54)
        6.5->7 - 5 (59)
        '''
        x = power
        x2 = x * x
        x3 = x * x * x
        y = -0.2542484+19.04314*x-3.04981*x2+0.2183677*x3
        y = clamp(y, 0.0, 59.0)
        return y    
    
    # Power [0,7]
    def calc_power_to_duration_frames_60fps(self, power):
        '''
        0 - 0
        0.5 - 9
        1 - 14
        1.5 - 19
        2 - 23
        2.5 - 26
        3 - 29
        3.5 - 32
        4 - 34
        4.5 - 36
        5 - 39
        5.5 - 41
        6 - 44
        6.5 - 46
        7 - 49
        '''
        x = power
        x2 = x * x
        x3 = x * x * x
        y = 0.9767974 + 14.96088*x - 2.337176*x2 + 0.1697671*x3
        y = clamp(y, 0.0, 54.0)
        return y

    # return [0,7] for the power bar
    def calc_power_from_t(self, target_t):
        if self.manual_power > -1:
            return self.manual_power
        
        x = clamp(target_t, 0.0, 1.0)
        x2 = x * x
        x3 = x * x * x
        x4 = x * x * x * x
        # [0,1] --> [0,7] 
        y = -0.02296112 + 13.05201*x - 17.08267*x2 + 19.2949*x3 - 8.234926*x4
        y = clamp(y, 0.0, 7.0)

        return y
    
    def power_to_durationms_60fps(self, power):

        '''
        bias=0.25
        scale=1.02
        (input) power_got | ms (time_held)
        (1)0.75 277
        (2)1.75 418
        (3)2.75 519
        (4)3.5  596
        (5)4.1  672
        (6)5.3  756
        (7)6.9  875

        (input) power_got | ms (time_held)
        (1)0.5  230
        (2)1.5  382
        (3)2.5  490
        (4)3.25 572
        (5)4    643
        (6)4.9  722
        (7)6.1  824

        
        # Combined all points
        power | ms (time_held)
        0.5     230
        0.75    277
        1.5     382
        1.75    418
        2.5     490
        2.75    519
        3.25    572
        3.5     596
        4.0     643
        4.1     672
        4.9     722
        5.3     756
        6.1     824
        6.9     875
        '''

        x = clamp(power, 0.0, 7.0)
        x2 = x * x
        x3 = x * x * x

        y = 158.4975+162.7539*x-12.40571*x2+0.5690662*x3

        return y
    
    # Returns ms to hold down input for a given [0,7] power
    def calc_duration_from_power(self, power):
        # y = self.poly4th_approx(power)
        # duration_ms = self.calc_power_to_duration_frames_60fps(power) * 1000.0/ 60.0
        duration_ms = self.power_to_durationms_60fps(power)

        duration_ms = min(duration_ms, 890)
        return duration_ms
    
    # returns frames @60fps
    def poly4th_approx(self, power):
        x = clamp(float(power), 0.0, 7.0)
        x2 = x * x
        x3 = x * x * x
        x4 = x * x * x * x
        # frames in 60fps to hold down button
        y = 0.1136364 + 18.17587*x - 4.323864*x2 + 0.6174242*x3 - 0.03219697*x4
        return y
    
    # returns frames @60fps
    def quadric_approx(self, power):
        x = clamp(float(power), 0.0, 7.0)
        x2 = x * x
        y = 2.25 + 10.95238*x - 0.6190476*x2
        return y
    
    '''
    power - frames

    1 - 38
    1.5 - 43
    2 - 45
    2.5 - 48
    3 - 49
    4 - 55
    ?4.1 - 56
    4.5 - 58
    ?4.8 - 59
    5.1 - 61
    5.5 - 64
    6.9 - 69
    '''
    def air_time_from_power_60fps(self, power):
        x = power
        x2 = x * x
        x3 = x * x * x
        y = 32.81027 + 6.199249*x - 0.1308308*x2

        return y
    
    def air_time_from_power_seconds(self, power):
        frames = self.air_time_from_power_60fps(power)

        seconds = frames / 60
        return seconds

    def force_update_selected_index_data(self):
        found_some = False
        for i in range(1,4):
            if self.fishing_state.selected_target == i:
                found_some = True
                rect = self.get_target_rect_index(i)
                prev_y = rect[1]
                prev_w = rect[2]
                prev_h = rect[3]

                t_transformed_to_pixels = self.fishing_state.selected_target_left_t * float(self.total_reachable_dist)
                t_transformed_to_pixels = t_transformed_to_pixels + self.dist_unreachable_left + self.waterrange_rect[0]

                start_x = t_transformed_to_pixels
                #translate half
                start_x = start_x - prev_w * 0.5

                if i == 1:
                    self.target1_rect = (int(start_x), int(prev_y), int(prev_w), int(prev_h))
                elif i == 2:
                    self.target2_rect = (int(start_x), int(prev_y), int(prev_w), int(prev_h))
                elif i == 3:
                    self.target3_rect = (int(start_x), int(prev_y), int(prev_w), int(prev_h))
                elif i == 4:
                    self.target1_rect = (int(start_x), int(prev_y), int(prev_w), int(prev_h))

        if not found_some:
            print("Something went wrong")

    def run(self, img_frame):
        # img_frame = self.test.copy()

        current_time = time.perf_counter()
        if self.fishing_state.state == fishing_state_init:
            (found_waterrange, waterrange_rect) = self.find_waterrange_rect(img_frame)
            if found_waterrange:
                self.waterrange_rect = waterrange_rect
            (found_bar, bar_rect) = self.find_bar_rect(img_frame)
            if found_waterrange:
                self.bar_rect = bar_rect

            self.fishing_state.selected_target = 0
            self.fishing_state.level_count = 0
            self.fishing_state.whale_count = 0

            # Should we start the machine?
            if found_waterrange and found_bar:
                self.closest_distance_to_mine = -1.0
                self.fishing_state.state = fishing_state_idle
                self.fishing_state.selected_target = 0
                self.fishing_state.timestamp_collect_target_t = -1.0

                debug_draw_rectangle(img_frame, self.waterrange_rect, self.color_waterrange)
                debug_draw_rectangle(img_frame, self.bar_rect, self.color_waterrange)

        elif self.fishing_state.state == fishing_state_idle:
            (found_waterrange, waterrange_rect) = self.find_waterrange_rect(img_frame)
            if found_waterrange:
                self.waterrange_rect = waterrange_rect
            (found_bar, bar_rect) = self.find_bar_rect(img_frame)
            if found_waterrange:
                self.bar_rect = bar_rect

            self.fishing_state.selected_target = 0

            # Should we start the machine?
            if found_waterrange and found_bar:
                self.closest_distance_to_mine = -1.0
                self.fishing_state.state = fishing_state_choose_target
                self.fishing_state.timestamp_collect_target_t = -1.0
                self.fishing_state.selected_target = 0

                debug_draw_rectangle(img_frame, self.waterrange_rect, self.color_waterrange)
                debug_draw_rectangle(img_frame, self.bar_rect, self.color_waterrange)

        elif self.fishing_state.state == fishing_state_choose_target:
            if self.fishing_state.timestamp_collect_target_t == -1.0:
                self.fishing_state.timestamp_collect_target_t = time.perf_counter()

            # self.update_avoidtarget_rects(img_frame)
            for i in range(1, 5):
                self.update_target(img_frame, i)

            (best_target, best_target_rect) = self.find_catch_target(img_frame)
            self.fishing_state.selected_target = max(best_target, self.fishing_state.selected_target)

            duration_since_state_start = current_time - self.fishing_state.timestamp_collect_target_t
            duration_total_this_state = 3.0
            
            if best_target != 0 and duration_since_state_start >= duration_total_this_state:
                target_t = self.find_target_t(self.get_target_rect_index(self.fishing_state.selected_target))

                self.fishing_state.state = fishing_state_collect_target_t
                self.fishing_state.selected_target_left_t = target_t
                self.fishing_state.selected_target_right_t = target_t
                self.fishing_state.timestamp_selected_target = time.perf_counter()
                self.fishing_state.selected_target_left_t_timestamp = -1.0
                self.fishing_state.selected_target_right_t_timestamp = -1.0

            debug_draw_rectangle(img_frame, self.waterrange_rect, self.color_waterrange)
            debug_draw_rectangle(img_frame, self.bar_rect, self.color_waterrange)
            self.debug_draw_dist_rects(img_frame)
            self.debug_draw_targets(img_frame)
            self.draw_all_t(img_frame)


        elif self.fishing_state.state == fishing_state_collect_target_t:
            # self.update_avoidtarget_rects(img_frame)
            (found, rect) = self.find_target(img_frame, self.fishing_state.selected_target)
            if not found:
                print("Target: %d was not found each frame" % (self.fishing_state.selected_target))
                return

            t = self.find_target_t(rect)

            if t <= self.fishing_state.selected_target_left_t:
                self.fishing_state.selected_target_left_t = t
                self.fishing_state.selected_target_left_t_timestamp = current_time
            elif t >= self.fishing_state.selected_target_right_t:
                self.fishing_state.selected_target_right_t = t
                self.fishing_state.selected_target_right_t_timestamp = current_time
            
            duration_since_state_start = current_time - self.fishing_state.timestamp_selected_target
            duration_total_this_state = 6.0
            if duration_since_state_start >= duration_total_this_state:
                if self.fishing_state.selected_target_left_t_timestamp == -1.0:
                    self.fishing_state.selected_target_left_t_timestamp = self.fishing_state.selected_target_right_t_timestamp
                if self.fishing_state.selected_target_right_t_timestamp == -1.0:
                    self.fishing_state.selected_target_right_t_timestamp = self.fishing_state.selected_target_left_t_timestamp
                    
                self.fishing_state.timestamp_do_input = time.perf_counter()
                self.fishing_state.decided_input = FishingDecidedInput()
                self.fishing_state.state = fishing_state_do_input
            else:
                # Debug Draw selected target
                debug_target_rect = self.get_target_rect_index(self.fishing_state.selected_target)
                debug_target_color = self.get_target_color_index(self.fishing_state.selected_target)
                debug_draw_rectangle(img_frame, debug_target_rect, debug_target_color)
                debug_dist_2_target_rect = self.get_dist_2_target_rect(debug_target_rect)
                debug_draw_rectangle(img_frame, debug_dist_2_target_rect, debug_target_color)

                # Draw t
                t = self.find_target_t(debug_target_rect)
                x_nudge = -50
                y_nudge = 30
                pos_x = debug_target_rect[0] + debug_target_rect[2]
                pos_y = self.waterrange_rect[1] + self.waterrange_rect[3]
                pos_y += y_nudge
                pos_y = int(pos_y)
                sub_string_len = 3
                debug_draw_text(img_frame,
                        str(t)[0:sub_string_len+1],
                        (pos_x+x_nudge, pos_y))
                power = self.calc_power_from_t(t)
                debug_draw_text(img_frame,
                        str(power)[0:sub_string_len+1],
                        (pos_x+x_nudge, pos_y + 30))


        elif self.fishing_state.state == fishing_state_do_input:
            if not globals.accepting_input:
                self.fishing_state.state = fishing_state_idle
                return

            globals.performance_critical = True

            if globals.catching_megalodon:
                if self.fishing_state.selected_target == 5:
                    stall_until_manual_interupt = True
                    if stall_until_manual_interupt:
                        print("Megalodon found, catch manually...")
                        time.sleep(999999999)

            if not self.fishing_state.decided_input.isDecided:
                self.force_update_selected_index_data()
                duration = current_time - self.fishing_state.timestamp_do_input

                min_t = self.fishing_state.selected_target_left_t
                t = min_t

                (min_t_timestamp, max_t_timestamp) = get_min_max(self.fishing_state.selected_target_left_t_timestamp, self.fishing_state.selected_target_right_t_timestamp)
                t_timestamp = self.fishing_state.selected_target_left_t_timestamp
                t_timestamp_diff = max_t_timestamp - min_t_timestamp
                # If case missing min/max t_timestamp information fully, 
                t_timestamp_diff = max(t_timestamp_diff, 2.6)

                power = self.calc_power_from_t(t)
                print("Calculating DecidedInput for (t,power,time_between_ts): (%f, %f, %f)" % (float(t), float(power), float(t_timestamp_diff)))
                duration_from_pow_ms = self.calc_duration_from_power(power)
                print("Duration from power: %f" % duration_from_pow_ms)
                air_time = self.air_time_from_power_seconds(power)
                print("Calculated Air Time: %f" % air_time)

                next_time = t_timestamp
                wait_time = 0
                # if target moves
                if t_timestamp_diff > 0.01:
                    next_time = t_timestamp + max(t_timestamp_diff, 0.0)*2.0
                    next_time = next_time - (air_time + duration_from_pow_ms / 1000.0)
                    wait_time = next_time - current_time
                    if wait_time <= 0.0:
                        print("waiting time <= 0.0 detected!, retrying...")
                        self.fishing_state.state = fishing_state_choose_target
                        self.fishing_state.timestamp_collect_target_t = -1.0
                        self.fishing_state.selected_target = 0
                        return
                

                print("Waiting %f sec..." % wait_time)

                self.fishing_state.decided_input.isDecided = True
                self.fishing_state.decided_input.timestamp_decided = current_time
                self.fishing_state.decided_input.hold_duration_ms = duration_from_pow_ms
                self.fishing_state.decided_input.power = power
                self.fishing_state.decided_input.t = t
                self.fishing_state.decided_input.timestamp_start_holding = next_time
                self.fishing_state.decided_input.timestamp_stop_holding = next_time + (duration_from_pow_ms/1000.0)

            elif current_time >= self.fishing_state.decided_input.timestamp_start_holding:
                #debug
                if abs(current_time - self.fishing_state.decided_input.timestamp_start_holding) >= 2.0:
                    print("Error!: Will start holding with diff >= 2ms, %f" % (current_time - self.fishing_state.decided_input.timestamp_start_holding))

                decided_input_diff = self.fishing_state.decided_input.timestamp_stop_holding - self.fishing_state.decided_input.timestamp_start_holding
                decided_input_diff_ms = decided_input_diff * 1000.0
                if abs(decided_input_diff_ms - self.fishing_state.decided_input.hold_duration_ms) > 0.5:
                    print("Error!!!: decided_input Hold Duration/Time diff")
                    print("decided_input_diff_ms %f" % decided_input_diff_ms)
                    print("hold_duration_ms %f" % self.fishing_state.decided_input.hold_duration_ms)

                print("Holding Space for %f ms" % self.fishing_state.decided_input.hold_duration_ms)
                self.fishing_state.decided_input.timestamp_started_holding = time.perf_counter()
                SpaceDown()
                # is consistently 1 ms too slow to release
                measured_time_bias = 0.001
                stall(-measured_time_bias + self.fishing_state.decided_input.hold_duration_ms / 1000.0)
                SpaceUp()
                elapsed = time.perf_counter() - self.fishing_state.decided_input.timestamp_started_holding
                print("Released Space, Time held: %f ms" % (float(elapsed * 1000.0)))

                self.fishing_state.state = fishing_state_wait_for_new_round
                self.fishing_state.timestamp_wait_new_round = time.perf_counter()
  
        elif self.fishing_state.state == fishing_state_wait_for_new_round:
            globals.performance_critical = False

            # Debug Draw aimed at target
            debug_target_color = (219, 169, 103)
            debug_target_rect = self.get_target_rect_index(self.fishing_state.selected_target)
            debug_x = self.t_to_waterrange(self.fishing_state.decided_input.t) - debug_target_rect[2] * 0.5
            debug_target_rect = (debug_x, debug_target_rect[1], debug_target_rect[2], debug_target_rect[3])
            debug_draw_rectangle(img_frame, debug_target_rect, (debug_target_color))
            debug_dist_2_target_rect = self.get_dist_2_target_rect(debug_target_rect)
            debug_draw_rectangle(img_frame, debug_dist_2_target_rect, debug_target_color)
            
            duration = current_time - self.fishing_state.timestamp_wait_new_round
            wait_new_round_delay_seconds = 6.0

            if duration >= wait_new_round_delay_seconds:
                (found_bar, bar_rect) = self.find_bar_rect(img_frame)
                if found_bar:
                    self.bar_rect = bar_rect
                    debug_draw_rectangle(img_frame, self.bar_rect, self.color_waterrange)

                (found_waterrange, waterrange_rect) = self.find_waterrange_rect(img_frame)
                if found_waterrange:
                    self.waterrange_rect = waterrange_rect
                    debug_draw_rectangle(img_frame, self.waterrange_rect, self.color_waterrange)
                
                if found_waterrange and found_bar:
                    # Set Whale Third Missed
                    if self.fishing_state.selected_target < 4:
                        if self.fishing_state.whale_count == 2:
                            self.fishing_state.whale_third_missed = True

                    self.fishing_state.level_count += 1
                    if self.fishing_state.selected_target == 4:
                        self.fishing_state.whale_count += 1                    
                    elif self.fishing_state.selected_target == 5:
                        self.fishing_state.megalodon_count += 1
                    self.fishing_state.reset()
                    self.fishing_state.state = fishing_state_choose_target

        if not globals.performance_critical:
            if globals.show_hud:
                self.debug_draw(img_frame)

    # return [0,1] the distance from shore to end
    def find_target_t(self, target_rect):
        target = rect_center(target_rect)
        
        t = self.waterrange_to_t(target[0])
        return t
    

    def t_to_waterrange(self, t: float):
        s = (t * float(self.total_reachable_dist)) + self.dist_unreachable_left
        x = s + self.waterrange_rect[0]
        return x

    def waterrange_to_t(self, x: float):
        dist_from_shore = x - self.waterrange_rect[0]
        t = float(dist_from_shore - self.dist_unreachable_left) / float(self.total_reachable_dist) 
        return t


