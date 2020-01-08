#! /usr/bin/env python

import os
import sys
from skimage import io
import requests
import re
import json
from bs4 import BeautifulSoup
import notifications
import parse_img
from resort_names import *
import SQLitedb as sql
import time
import cache
from dotenv import load_dotenv, find_dotenv
from logger import *

_date = time.strftime("%Y%m%d")
_time = time.strftime("%H%M%S")
g_date = f"{_date}_{_time}"

curr_dir = os.path.dirname(os.path.realpath(__file__))
webcam_dir = f"{curr_dir}/log/CAM"
webpage_dir = f"{curr_dir}/log/HTML"

load_dotenv(find_dotenv())
PLOT_DEBUG = os.environ.get("DEBUG", False)


class Resort:

    def __init__(self, name, local_resort, cam_url=None, info_url=None):
        self.name = name or "default"
        self.webcam_url = cam_url
        self.info_url = info_url
        self.webcam_img = None
        self._24hsnow = ""
        self._12hsnow = ""
        self.overnight_cam = ""
        self.extra_info = ""
        self.local_resort = local_resort or False

    def update(self):
        log.debug(f"Retrieve {self.name} data")
        if self.webcam_url:
            log.debug(f"{self.name}: Webcam detected")
            self.webcam_img = io.imread(self.webcam_url)
            self.overnight_cam = parse_img.read_height(image=self.webcam_img,
                                                  debug_option=PLOT_DEBUG,
                                                  resort=self.name)
            webcam_name = f"{g_date}_{self.name.title()}_cam.png"
            log.debug(f"{self.name}: Save webcam in {webcam_dir} as {webcam_name}")
            io.imsave(f"{webcam_dir}/{webcam_name}", self.webcam_img)
        page = requests.get(self.info_url)

        if (page.status_code != 200):
            self.extra_info = "N/A"
            return

        webpage_name = (f"{g_date}_{self.name.title()}.html")
        log.debug(f"{self.name}: Save HTML page in {webpage_dir} as {webpage_name}")
        with open(f"{webpage_dir}/{webpage_name}", "w") as html_log_file:
            html_log_file.write(page.text)

        handler_fnc = getattr(self, f'update_{self.name}')
        return handler_fnc(page)

    def update_whistler(self, page):
        log.debug(f"{self.name}: Parse website")
        text_json = re.search('FR.snowReportData = ({.*});', page.text)
        data = json.loads(text_json.groups()[0])
        self._24hsnow = data['TwentyFourHourSnowfall']['Centimeters']
        self._12hsnow = data['OvernightSnowfall']['Centimeters']
        log.debug(f"{self.name}: Snow: {self._12hsnow}cm (12h)   {self._24hsnow}cm (24h)")

    def update_cypress(self, page):
        log.debug(f"{self.name}: Parse website")
        soup = BeautifulSoup(page.content, 'html.parser')
        all_div = soup.find_all('div', class_='box')  # find 12h/24h/48h/7Days report
        for div in all_div:
            if "24Hr" in div.text and "cm" in div.text:
                snow = div.find('span', class_='js-measurement')
                self._24hsnow = snow.text
        log.debug(f"{self.name}: Snow: {self._24hsnow}cm (24h)")

    def update_mt_seymour(self, page):
        log.debug(f"{self.name}: Parse website")
        soup = BeautifulSoup(page.content, 'html.parser')
        all_td = soup.find_all('td')
        for td in all_td:
            if "Last 24 hours" in td.text:
                snow = td.text.split(' ')[3]
                self._24hsnow = re.sub('[a-z]', '', snow)
                break
        log.debug(f"{self.name}: Snow: {self._24hsnow}cm (24h) (no 12h data)")

    def update_mt_baker(self, page):
        log.debug(f"{self.name}: Parse website")
        soup = BeautifulSoup(page.content, 'html.parser')
        div = soup.find('div', class_='report-snowfall-value-12')

        # Syntax div.text: '\n3″\n7.62cm\n'
        snow = re.sub('\n', '', div.text)
        snow = re.sub('[a-z]','',snow)
        self._12hsnow = snow.split('″')[1].split('.')[0]

        div = soup.find('div', class_='report-snowfall-value-24')
        snow = re.sub('\n', '', div.text)
        snow = re.sub('[a-z]', '', snow)
        self._24hsnow = snow.split('″')[1].split('.')[0]
        log.debug(f"{self.name}: Snow: {self._12hsnow}cm (12h)   {self._24hsnow}cm (24h)")

    def update_mt_cain(self, page):
        log.debug(f"{self.name}: Parse website")
        soup = BeautifulSoup(page.content, 'html.parser')
        all_p = soup.find_all('p')

        # Syntax -> New Overnight: 0cm - 0in
        for p in all_p:
            if "Overnight" in p.text:
                snow = p.text.split(':')[1].split('-')[0].strip()
                self._12hsnow = re.sub('[a-z]', '', snow)
            if "24hrs" in p.text:
                snow = p.text.split(':')[1].split('-')[0].strip()
                self._24hsnow = re.sub('[a-z]', '', snow)
        log.debug(f"{self.name}: Snow: 12h:{self._12hsnow}cm   24h:{self._24hsnow}cm")

    def display_info(self):
        print(f"{self.name.title()} report:")
        print(f"{self.snowcam} cm overnight")
        print(f"{self._12hsnow} cm last 12h")
        print(f"{self._24hsnow} cm last 24h")
        print(f"Special resort info: {self.extra_info} ")
        print("******************")

    @property
    def data(self):
        self.update()
        return {'name':self.name,
                '12':self._12hsnow,
                '24':self._24hsnow,
                'snowcam':self.overnight_cam,
                'info':self.extra_info,
                'local':self.local_resort}


resort_dict = {
    CYPRESS: Resort(name=CYPRESS,
                    cam_url="http://snowstakecam.cypressmountain.com/axis-cgi/jpg/image.cgi?resolution=1024x768",
                    info_url="http://www.cypressmountain.com/downhill-conditions-and-cams",
                    local_resort=True),

    SEYMOUR: Resort(name=SEYMOUR,
                    info_url="http://mtseymour.ca/conditions-hours-operation",
                    local_resort=True),

    WHISTLER: Resort(name=WHISTLER,
                     info_url="https://www.whistlerblackcomb.com/the-mountain/mountain-conditions/snow-and-weather-report.aspx",
                     local_resort=True),

    BAKER: Resort(name=BAKER,
                  info_url="https://www.mtbaker.us/snow-report",
                  local_resort=False),

    CAIN: Resort(name=CAIN,
                 info_url="http://www.mountcain.com/pages/snowreport/cain_snowreport.cfm",
                 local_resort=False)
}


def check_snow(resort_list_names=None):
    names = resort_list_names or resort_dict.keys()
    result = []
    for name in names:
        result.append(resort_dict[name].data)
    return result

def prettify_data(data_list_of_dict):
    txt = "**Snow Report**"
    for resort in data_list_of_dict:
        txt = f"{txt}\n{re.sub('_', ' ', resort['name']).title()}:"

        if resort['info'] == 'N/A':
            txt = f"{txt}\nData Not Available"
        else:
            if resort['name'] == CYPRESS:
                try:
                    int(resort['12'])
                except ValueError:  # Meaning the value can be 'Trace' or n/a etc.
                    resort['12'] = 0
                try:
                    int(resort['24'])
                except ValueError:  # Meaning the value can be 'Trace' or n/a etc.
                    resort['24'] = 0

            if resort['snowcam']:
                txt = f"{txt}\n{resort['snowcam']}cm overnight (snow cam)"
            if resort['12']:
                txt = f"{txt}\n{resort['12']}cm last 12h"
            if resort['24']:
                txt = f"{txt}\n{resort['24']}cm last 24h"
            if resort['info']:
                txt = f"{txt}\nSPECIAL NOTICE: {resort['info']}"
        txt = f"{txt}\n******************"

    return txt


# This entry point is ran only in the morning for registered numbers
if __name__ == "__main__":
    fresh_snow = False
    registered_numbers = sql.query_registered_numbers()

    cache_resorts_list = cache.get()

    # pop out the non local resorts from the list
    cache_resorts_list = [resort for resort in cache_resorts_list if resort['local']]

    for resort in cache_resorts_list:
        if resort['12'] and int(resort['12']) > 0: # Mt Seymour doesnt have a 12h snow report
            fresh_snow = True

    if fresh_snow:
        txt = prettify_data(cache_resorts_list)
        for number in registered_numbers:
            notifications.send_sms(txt, number)


