#! /usr/bin/env python

import os
import cv2
import numpy as np
from matplotlib import pyplot as plt
from dotenv import load_dotenv, find_dotenv
from logger import *


load_dotenv(find_dotenv())
curr_dir = os.path.dirname(os.path.realpath(__file__))

cypress_cal_img =f"{curr_dir}/templates/SnowStake_Cypress_night0.jpg"
cypress_top_template_img = f"{curr_dir}/templates/40.jpg"
cypress_base_template_img = f"{curr_dir}/templates/base.jpg"


# All the 6 methods for comparison
methods = ['cv2.TM_CCOEFF', 'cv2.TM_CCOEFF_NORMED', 'cv2.TM_CCORR',
            'cv2.TM_CCORR_NORMED', 'cv2.TM_SQDIFF', 'cv2.TM_SQDIFF_NORMED']


def cypress_img(debug_option=False):
    log.debug("Calibrate Cypress webacam")
    log.debug(f"Template images used to perform calibration: \n" \
        f" - Webcam: {cypress_cal_img}\n" \
        f" - Top ROI: {cypress_top_template_img}\n" \
        f" - Bottom ROI: {cypress_base_template_img}")

    # the following image will be used to calibrate the scale
    img = cv2.imread(cypress_cal_img, 0)
    img2 = img.copy()
    template1 = cv2.imread(cypress_top_template_img, 0)
    template2 = cv2.imread(cypress_base_template_img, 0)

    log.debug("Resize templates by a 1:2 factor to accomodate Apple grab tool effect")
    template1 = cv2.resize(template1, (0, 0), fx=0.5, fy=0.5)
    template2 = cv2.resize(template2, (0, 0), fx=0.5, fy=0.5)
    h1, w1 = template1.shape
    h2, w2 = template2.shape

    if debug_option:
        # allows to pick which method works best
        for meth in methods:
            img = img2.copy()
            method = eval(meth)

            # Apply template Matching
            res = cv2.matchTemplate(img, template1, method)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

            # If the method is TM_SQDIFF or TM_SQDIFF_NORMED, take minimum
            if method in [cv2.TM_SQDIFF, cv2.TM_SQDIFF_NORMED]:
                top_left = min_loc
            else:
                top_left = max_loc
            bottom_right = (top_left[0] + w1, top_left[1] + h1)

            cv2.rectangle(img, top_left, bottom_right, 255, 2)

            plt.subplot(111), plt.imshow(img, cmap='gray')
            plt.title(meth), plt.xticks([]), plt.yticks([])
            plt.show()

        print("TM_CCOEFF_NORMED is best method (or equivalent to TM_CCORR_NORMED, TM_SQDIFF, TM_SQDIFF_NORMED)")
        print("TM_CCORR is the worst")

    debug.log("Use TM_CCOEFF_NORMED method to find template ROI images on calibration image")
    method = eval('cv2.TM_CCOEFF_NORMED')
    img = img2.copy()
    res1 = cv2.matchTemplate(img, template1, method)
    res2 = cv2.matchTemplate(img, template2, method)

    debug.log("Extract the 4 coordinates for the whole ROI")
    min_val1, max_val1, min_loc1, max_loc1 = cv2.minMaxLoc(res1)
    min_val2, max_val2, min_loc2, max_loc2 = cv2.minMaxLoc(res2)
    top_left1 = max_loc1
    top_left2 = max_loc2
    bottom_right1 = (top_left1[0] + w1, top_left1[1] + h1)
    bottom_right2 = (top_left2[0] + w2, top_left2[1] + h2)

    if debug_option:
        roi_top_left = top_left1
        roi_top_right = (top_left1[0] + w1, top_left1[1])
        roi_bottom_right = bottom_right2
        roi_bottom_left = (bottom_right2[0] - w2, bottom_right2[1])

        cv2.rectangle(img, top_left1, bottom_right1, 255, 2)
        cv2.rectangle(img, top_left2, bottom_right2, 255, 2)

        points = [
            list(roi_top_left),
            list(roi_top_right),
            list(roi_bottom_right),
            list(roi_bottom_left)
            ]

        # Now plot the ROI
        pts = np.array(points, np.int32)
        cv2.polylines(img, [pts], True, (255, 255, 255), thickness=5)

        plt.subplot(111), plt.imshow(img, cmap='gray')
        plt.title('ROI'), plt.xticks([]), plt.yticks([])
        plt.show()

    top_left_offset = (0, 0)
    top_right_offset = (w1, 0)
    bottom_left_offset = ((bottom_right2[0] - w2) - top_left1[0], bottom_right2[1] - top_left1[1])
    bottom_right_offset = (bottom_right2[0] - top_left1[0], bottom_right2[1] - top_left1[1])

    log.debug("Update .env file with the offset to apply to get the 4 corners of the ROI")
    log.debug("TOP_LEFT_OFFSET=\""+str(top_left_offset)+"\"\n" \
        "TOP_RIGHT_OFFSET=\"" + str(top_right_offset) + "\"\n" \
        "BOTTOM_LEFT_OFFSET=\"" + str(bottom_left_offset) + "\"\n" \
        "BOTTOM_RIGHT_OFFSET=\"" + str(bottom_right_offset) + "\"\n")

    with open(".env", 'a') as env:
        env.write("\n")
        env.write("TOP_LEFT_OFFSET=\""+str(top_left_offset)+"\"\n")
        env.write("TOP_RIGHT_OFFSET=\"" + str(top_right_offset) + "\"\n")
        env.write("BOTTOM_LEFT_OFFSET=\"" + str(bottom_left_offset) + "\"\n")
        env.write("BOTTOM_RIGHT_OFFSET=\"" + str(bottom_right_offset) + "\"\n")

