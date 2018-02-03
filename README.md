# pow_alert

Automated script that parse recent snow falls from Vancouver local mountain resort websites and send a text message with the information. So far only Whistler and Cypress are being taken care of. Possibility to add new resorts easily if needed.

POWalert_malc.py parses the resorst's URL and extracts information from the webpages when possible. Otherwise will extract snow-cam images to image process them.
Then it will call parse_img.py with the snow-cam image as parameter

(So far only handles Cypress' snow-cam)
parse_img.py will check if we already established a calibration/work-frame to work on the image. These information are available in .env file
if .env file doesnt have the info (first time going thru the script) then, calibrate.py is called and the ROI_offset are calculated. Those information will be stored in .env and the program will go back to parse_img.py
parse_img.py has now acces to .env new data and can calculate the ROI to work on.
(of course if the data were already there the above process is not executed)
The main purpose of doing so is to handle potential mouvement in the snow-cam footage. The code is written to be able to find the ROI even if the snow-cam as moved.

TODO: Process image in the ROI to extract info.

Once parse_img.py the script comes back to POWalert_malc which will update its class and call send_text.py which will send a text with the usefull information.

TODO: Make that README nicer
