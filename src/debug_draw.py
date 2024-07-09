import cv2
import numpy as np
from misc import *

def debug_draw_circle(frame_img, pos_xy, radius, color_bgr = (0,255,255)):
    cv2.circle(frame_img, (int(pos_xy[0]), int(pos_xy[1])), radius, color_bgr, radius*2)

def debug_draw_rectangle(frame_img, rectangle, color = (0,255,255)):    
    (x,y,w,h) = rectangle

    x = int(x)
    y = int(y)
    w = int(w)
    h = int(h)

    cv2.rectangle(frame_img, (x,y), (x+w, y+h), color, 2)

def debug_draw_rects(frame_img, rects, color = (0,255,255)):
    for rectangle in rects:
        debug_draw_rectangle(frame_img, rectangle, color)


def debug_draw_match_results(frame_img, match_img, locs_x, locs_y):
    group_threshold = 0.2
    template_w = match_img.shape[1]
    template_h = match_img.shape[0]
    rects = gather_match_results(template_w, template_h, locs_x, locs_y, group_threshold)
    
    for rectangle in rects:
        debug_draw_rectangle(frame_img, rectangle)


def debug_draw_text(img_frame, text, bottomLeftCornerOfText = (100, 40), color = (0, 255, 0), fontScale = 1, thickness = 2):  
    font                   = cv2.FONT_HERSHEY_SIMPLEX
    bottomLeftCornerOfText = (int(bottomLeftCornerOfText[0]), int(bottomLeftCornerOfText[1]))
    fontScale              = fontScale
    fontColor              = color
    thickness              = thickness
    lineType               = 2
    cv2.putText(img_frame, text, 
        bottomLeftCornerOfText, 
        font, 
        fontScale,
        fontColor,
        thickness,
        lineType)