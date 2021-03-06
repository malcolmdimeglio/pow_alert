#! /usr/bin/env python

import os
import cv2
import calibrate
import collections
from resort_names import *
from dotenv import load_dotenv, find_dotenv
from logger import *

Params = collections.namedtuple('Params', ['a', 'b', 'c'])  # to store equation of a line
WHITE_THRESHOLD = 0.5 * 255
LIST_OF_THRESHOLDS = ('40', '35', '30', '25', '20', '15', '10', '5', '0')
NBR_OF_THRESHOLD = len(LIST_OF_THRESHOLDS) - 1
curr_dir = os.path.dirname(os.path.realpath(__file__))
cypress_top_template_img = f"{curr_dir}/templates/40.jpg"
cypress_base_template_img = f"{curr_dir}/templates/base.jpg"

curr_dir = os.path.dirname(os.path.realpath(__file__))


def calc_params(point1, point2):  # line's equation Params computation aX + bY + c
    if point2[1] - point1[1] == 0:
        a = 0
        b = -1.0
    elif point2[0] - point1[0] == 0:
        a = -1.0
        b = 0
    else:
        a = (point2[1] - point1[1]) / (point2[0] - point1[0])
        b = -1.0

    c = (-a * point1[0]) - b * point1[1]
    return Params(a, b, c)


def lines_intersection_pt(params1, params2, point1, point2, img, dbg):
    det = params1.a * params2.b - params2.a * params1.b
    if det == 0:
        return False  # lines are parallel
    else:
        x = round(((params2.b * -params1.c - params1.b * -params2.c)/det), 12)  # floating imprecision
        y = round(((params1.a * -params2.c - params2.a * -params1.c)/det), 12)  # floating imprecision
        if min(point1[0], point2[0]) <= x <= max(point1[0], point2[0]) \
                and min(point1[0], point2[0]) <= y <= max(point1[1], point2[1]):
            if dbg:
                cv2.circle(img, (int(x), int(y)), 10, (255, 255, 255), -1)  # intersecting point
            return int(x), int(y)  # lines are intersecting inside the line segment
        else:
            return  # lines are intersecting but outside of the line segment


def read_height(image, resort, debug_option=False):
    log.debug(f"Read {resort} snow fall level off webacam footage")
    if debug_option:
        from matplotlib import pyplot as plt

    if resort == CYPRESS:
        load_dotenv(find_dotenv())

        if os.environ.get("TOP_LEFT_OFFSET") is None:  # calibration has not been done, calibration is done once in a lifetime
            calibrate.cypress_img(debug_option)
            load_dotenv(find_dotenv())
        # else no need to calibrate > already done

        img = image
        img2 = img.copy()
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  # Otherwise the difference of encoding with cv2 and skimage will cause problems with matchTemplate
        template1 = cv2.imread(cypress_top_template_img, 0)

        log.debug("Resize templates by a 1:2 factor to accomodate Apple grab tool effect")
        template1 = cv2.resize(template1, None, fx=0.5, fy=0.5)  # MacOS grab.app changes resolution x2
        h1, w1 = template1.shape
        h, w = img.shape

        log.debug("Use TM_CCOEFF_NORMED method to find template ROI image coordinates on webcam image")
        method = eval('cv2.TM_CCOEFF_NORMED')
        res1 = cv2.matchTemplate(img, template1, method)
        min_val1, max_val1, min_loc1, max_loc1 = cv2.minMaxLoc(res1)
        top_left1 = max_loc1
        bottom_right1 = (top_left1[0] + w1, top_left1[1] + h1)

        log.debug("Extract from .env file the offsets to apply to get the ROI 4 corners")
        top_left_offset = eval(str(os.environ.get("TOP_LEFT_OFFSET")))
        top_right_offset = eval(str(os.environ.get("TOP_RIGHT_OFFSET")))
        bottom_left_offset = eval(str(os.environ.get("BOTTOM_LEFT_OFFSET")))
        bottom_right_offset = eval(str(os.environ.get("BOTTOM_RIGHT_OFFSET")))

        log.debug(f"TOP_LEFT_OFFSET={top_left_offset}")
        log.debug(f"TOP_RIGHT_OFFSET={top_right_offset}")
        log.debug(f"BOTTOM_LEFT_OFFSET={bottom_left_offset}")
        log.debug(f"BOTTOM_RIGHT_OFFSET={bottom_right_offset}")

        # Get 4 corners of ROI
        log.debug("Find all 4 (x,y) coordinates for main ROI:")
        roi_top_left = tuple(x + y for x, y in zip(top_left1, top_left_offset))
        roi_top_right = tuple(x + y for x, y in zip(top_left1, top_right_offset))
        roi_bottom_right = tuple(x + y for x, y in zip(top_left1, bottom_right_offset))
        roi_bottom_left = tuple(x + y for x, y in zip(top_left1, bottom_left_offset))
        log.debug(f"{roi_top_left}, {roi_top_right}, {roi_bottom_right}, {roi_bottom_left}")

        _top_mark_line = int((top_left1[1] + bottom_right1[1]) / 2)  # middle of the template (50cm) (y axis) Used as patient0
        _0_mark_line = roi_bottom_left[1]  # y axis on the ground
        log.debug(f"Top mark line at: {_top_mark_line}")
        log.debug(f"0 mark line at: {_0_mark_line}")

        # if we increase Y by thickness_scale, we get to the next threshold (5-10-15..50)
        thickness_scale = int(abs(_top_mark_line - _0_mark_line) / NBR_OF_THRESHOLD + 1)  # going from top to 0cm
        log.debug(f"Thickness between thresholds: {thickness_scale}")

        # Get the function of the 2 vertical ROI limits
        roi_left_line = calc_params(roi_top_left, roi_bottom_left)
        roi_right_line = calc_params(roi_top_right, roi_bottom_right)

        if debug_option:  # plots threshold lines
            offset = 0
            for i in range(NBR_OF_THRESHOLD):
                # black magic to counter difference of scale due to angle of camera
                if i == 1:
                    offset = 16
                if i == 2:
                    offset = 32
                if i == 3:
                    offset = 43
                if i == 4:
                    offset = 47
                if i == 5:
                    offset = 50
                if i == 6:
                    offset = 40
                if i == 7:
                    offset = 30
                cv2.line(img,
                         (5, int(_top_mark_line + (i * thickness_scale) + offset)),
                         (1020, int(_top_mark_line + (i * thickness_scale) + offset)),
                         (255, 255, 255),
                         5)
            plt.subplot(111), plt.imshow(img, cmap='gray')
            plt.title('Thresholds'), plt.xticks([]), plt.yticks([])
            plt.show()

        # extract points on both side of ROI where thresholds are
        threshold_points_list = list()
        offset = 0
        for i in range(NBR_OF_THRESHOLD):
            # black magic to counter the difference of scale due to angle of camera and may be also fish-eye
            if i == 1:
                offset = 16
            if i == 2:
                offset = 32
            if i == 3:
                offset = 43
            if i == 4:
                offset = 47
            if i == 5:
                offset = 50
            if i == 6:
                offset = 40
            if i == 7:
                offset = 30

            threshold_points = ((0, int(_top_mark_line + (i * thickness_scale) + offset)), (w-1, int(_top_mark_line + (i * thickness_scale) + offset)))
            threshold_line = calc_params((0, int(_top_mark_line + (i * thickness_scale) + offset)), (w-1, int(_top_mark_line + (i * thickness_scale) + offset)))

            img_dbg = img if debug_option else None
            point_a = lines_intersection_pt(roi_left_line, threshold_line, threshold_points[0], threshold_points[1],
                                            img_dbg, debug_option)
            point_b = lines_intersection_pt(roi_right_line, threshold_line, threshold_points[0], threshold_points[1],
                                            img_dbg, debug_option)

            threshold_points_list.append((point_a, point_b))
            log.debug(f"Threshold points for {LIST_OF_THRESHOLDS[i]}cm: ({point_a},{point_b})")

        if debug_option:
            plt.subplot(111), plt.imshow(img, cmap='gray')
            plt.title('Thresholds ROI limits'), plt.xticks([]), plt.yticks([])
            plt.show()

        if debug_option:
            img3 = img2.copy()

        # Extract ROI around threshold
        local_roi = list()
        for i in range(NBR_OF_THRESHOLD):
            if i < NBR_OF_THRESHOLD - 1:
                offset = i * 2  # Black magic to change ROI size because of the angle of the camera
                thick = abs(int((threshold_points_list[i][0][1] - threshold_points_list[i + 1][0][1]) / 2))

            # We want to apply a thickness slightly smaller on the way up, and slightly bigger on the way down (ratio 1/2:3/2), when creating the ROIs.
            # We also need to apply an offset to counter the angle of the camera.
            local_roi.append(img[int(threshold_points_list[i][0][1] - thick * (1/2)):int(threshold_points_list[i][1][1] + thick*(3/2) - offset),
                             threshold_points_list[i][0][0]:threshold_points_list[i][1][0]])

            if debug_option:
                cv2.rectangle(img3, (threshold_points_list[i][0][0], int(threshold_points_list[i][0][1] - thick* (1/2))),
                              (threshold_points_list[i][1][0], int(threshold_points_list[i][1][1] + thick* (3/2) - offset)), 255, 3)

        # Average value of pixels in the ROI
        avg_pix_roi = [int(roi.mean()) for roi in local_roi[:NBR_OF_THRESHOLD]]

        log.debug(f"White level threshold value: {WHITE_THRESHOLD}")
        for i, el in enumerate(avg_pix_roi):
            log.debug(f"ROI {LIST_OF_THRESHOLDS[i]}cm: white level: {el}")

        if debug_option:
            plt.subplot(111), plt.imshow(img3, cmap='gray')
            plt.title('ROI'), plt.xticks([]), plt.yticks([])
            plt.show()

        # Now scale it for snow fall
        for threshold_val, white_val in zip(LIST_OF_THRESHOLDS, avg_pix_roi):
            if white_val > WHITE_THRESHOLD:
                return threshold_val

        return LIST_OF_THRESHOLDS[-1]

