#! /usr/bin/env python

from urllib.request import urlopen
from skimage import io
import requests
import re
import json
from bs4 import BeautifulSoup
import send_text
import parse_img
import cv2


CYPRESS = "Cypress"
WHISTLER = "Whistler - Blackomb"


class Resort:

    def __init__(self, name, cam_url=None, info_url=None):
        self.name = name or "default"
        self.webcam_url = cam_url
        self.info_url = info_url
        self.webcam_img = None
        self._24hsnow = "???"
        self._12hsnow = "???"

    def update(self):
        if self.webcam_url:
            self.webcam_img = io.imread(self.webcam_url)#, as_grey=True)
            cv2.imshow('image1', self.webcam_img)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
            parse_img.main(self.webcam_img)

        page = requests.get(self.info_url)
        soup = BeautifulSoup(page.content, 'html.parser')

        if self.name == CYPRESS:
            all_div = soup.find_all('div', class_='weather-item clearfix')
            for div in all_div:
                if "24 hr Snow" in div.text:
                    el = div.find('span', class_='numbers')
                    self._24hsnow = el.text.split(' ')[0]

        if self.name == WHISTLER:
            text_json = re.search('FR.snowReportData = ({.*});', page.text)
            data = json.loads(text_json.groups()[0])
            self._24hsnow = data['TwentyFourHourSnowfall']['Centimeters']
            self._12hsnow = data['OvernightSnowfall']['Centimeters']

    @property
    def info(self):
        self.update()
        print(self.name+" report:")
        print(self._12hsnow+" cm overnight")
        print(self._24hsnow + " cm last 24h")
        print("*********")

<<<<<<< HEAD
=======
    @property
    def data(self):
        self.update()
        return self.name + " report:\n" + \
               self._12hsnow + " cm overnight\n" + \
               self._24hsnow + " cm last 24h\n" + \
               "******************\n"

>>>>>>> da05c82... from HTML scrapping to Json parsing

Resort_list = {Resort(name=CYPRESS,
                      cam_url="http://snowstakecam.cypressmountain.com/axis-cgi/jpg/image.cgi?resolution=1024x768",
                      info_url="http://www.cypressmountain.com/downhill-conditions/"),

               Resort(name=WHISTLER,
                      info_url="https://www.whistlerblackcomb.com/the-mountain/mountain-conditions/snow-and-weather-report.aspx")

               }

<<<<<<< HEAD
<<<<<<< HEAD
Cypress.info
Whistler.info

print(datetime.now() - startTime)

#with open('test.jpg', 'wb') as file:
#    file.write(cypress)



#
# # Find these values at https://twilio.com/user/account
# account_sid = os.environ.get("account_sid")
# auth_token = os.environ.get("auth_token")
#
# client = Client(account_sid, auth_token)
#
# client.api.account.messages.create(
#     to=os.environ.get("Malcolm_phone_nbr"),
#     from_=os.environ.get("Twilio_phone_nbr"),
#     body="attempt with dotenv")
=======
text_message = Cypress.data + Whistler.data
=======
txt_message = ""
for resort in Resort_list:
    txt_message = txt_message + resort.data
>>>>>>> 39ec0db... Massive architecture changes

send_text.main(txt_message)


<<<<<<< HEAD
client.api.account.messages.create(
    to=MALCOLM_PHONE_NUMBER,
    from_=TWILIO_PHONE_NUMBER,
    body=text_message)
>>>>>>> bf270fd... cosmetic
=======
>>>>>>> 39ec0db... Massive architecture changes
