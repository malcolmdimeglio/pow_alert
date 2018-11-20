#! /usr/bin/env python

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

day = time.strftime("%d")
month = time.strftime("%m")
year = time.strftime("%Y")
date = f"{year}_{month}_{day}"

PLOT_DEBUG = False

class Resort:

    def __init__(self, name, local_resort, cam_url=None, info_url=None):
        self.name = name or "default"
        self.webcam_url = cam_url
        self.info_url = info_url
        self.webcam_img = None
        self._24hsnow = ""
        self._12hsnow = ""
        self.extra_info = ""
        self.local_resort = local_resort or False

    def update(self):
        if self.webcam_url:
            self.webcam_img = io.imread(self.webcam_url)
            self._12hsnow = parse_img.read_height(image=self.webcam_img,
                                                  debug_option=PLOT_DEBUG,
                                                  resort=self.name)
            io.imsave(f"log/CAM/{date}_{self.name.title()}_cam.png", self.webcam_img)
        page = requests.get(self.info_url)
        with open(f"log/HTML/{date}_{self.name.title()}.html", "w") as html_log_file:
            html_log_file.write(page.text)

        handler_fnc = getattr(self, f'update_{self.name}')
        return handler_fnc(page)

    def update_whistler(self, page):
        text_json = re.search('FR.snowReportData = ({.*});', page.text)
        data = json.loads(text_json.groups()[0])
        self._24hsnow = data['TwentyFourHourSnowfall']['Centimeters']
        self._12hsnow = data['OvernightSnowfall']['Centimeters']

    def update_cypress(self, page):
        soup = BeautifulSoup(page.content, 'html.parser')
        all_div = soup.find_all('div', class_='flex_snowLocations')  # find 12h/24h/48h/7Days report
        for div in all_div:
            for all_subdiv in div.findAll('div'):  # cut each report separately
                if "24Hr" in all_subdiv.text:
                    el = all_subdiv.find('span', class_='js-measurement')
                    self._24hsnow = el.text
                if "12Hr" in all_subdiv.text:
                    el = all_subdiv.find('span', class_='js-measurement')
                    self._12hsnow = el.text

    def update_mt_seymour(self, page):
        soup = BeautifulSoup(page.content, 'html.parser')
        all_td = soup.find_all('td')
        for td in all_td:
            if "Last 24 hours" in td.text:
                fall = td.text.split(' ')[3]
                self._24hsnow = re.sub('[a-z]', '', fall)
                break

    def update_mt_baker(self, page):
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

    def update_mt_cain(self, page):
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

    def display_info(self):
        print(f"{self.name.title()} report:")
        print(f"{self._12hsnow} cm overnight")
        print(f"{self._24hsnow} cm last 24h")
        print(f"Special resort info: {self.extra_info} ")
        print("******************")

    @property
    def data(self):
        self.update()
        return {'name':self.name, '12':self._12hsnow, '24':self._24hsnow, 'info':self.extra_info, 'local':self.local_resort}


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

    # BAKER: Resort(name=BAKER,
    #               info_url="http://www.mtbaker.us/snow-report",
    #               local_resort=False),

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

        if resort['name'] == CYPRESS:
            try:
                int(resort['12'])
            except ValueError:  # Meaning the value can be 'Trace' or n/a etc.
                resort['12'] = 0
            try:
                int(resort['24'])
            except ValueError:  # Meaning the value can be 'Trace' or n/a etc.
                resort['24'] = 0

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
    try:
        PLOT_DEBUG = sys.argv[1]
    except IndexError:
        PLOT_DEBUG = False

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


