# pow_alert

Automated script/webapp hosted on a server that parse recent snow falls from Vancouver local mountain resort websites and send a text message with the information.

Pow_alert.py parses the resorst's URL and extracts information from the webpages when possible. Otherwise will extract snow-cam footages to image process them. (So far only need to handle Cypress' snow-cam)

## How to use it?
The interraction with the script/webapp is pretty straight forward. There is a few amount of key words you can use.
In order to get the phone number, please contact the developper.
Once you have the phone number (10-digit Vancouver, Canada based) you can text it anything.

### What Keywords can I use?
Here is the list of the keywords you can use
* 'Update': you will receive the information about the last 12h and last 24h snow fall on the local mountain
* 'Register': you will register for morning text if there has been some fresh snow on the local mountain. If no snow has fallen overnight, you will not receive a text.
* 'Unregister': If you don't want those early morning information you can unregister by sending this keywords
* 'Information': you will receive this list and explication of each keywords by text

### What if I send gibberish?
You can send ANYTHING to this number although, like mentioned previously, this webbapp only handles a few. if you send something that is not in the list above, you will receive a message reminding you what keywords are available to use.

### Is it case sensitive?
No. You can have cap letters. You can even shout 'UPDATE' if you're in the mood. You will still receive the update.

### Does it handles white space?
Yes. You can send 'Update ' or ' Update' or even ' Update '. It will make no difference.

### If I unregister, can I undo it?
Of course, you just have to send 'register' again and you will be all set for morning texts

### What resorts can I get the information of?
* Cypress Mountain - BC, CA
* Mt Seymour - BC, CA
* Whistler - Blackomb - BC, CA
* Mt Cain - BC, CA
* Mt Baker - WA, USA

If you are registered for the morning texts, you will only receive information concerning the Vancouver local mountains, such as Seymour, Cypress and Whistler-Blackomb.

If you send 'update' you will receive the information for all the resorts.

### What do the texts look like?
```
Update
```
```
**Snow Report**
Cypress:
0cm last 12h
1cm last 24h
******************
Mt Seymour:
4cm last 24h
******************
Whistler:
4cm last 12h
4cm last 24h
******************
Mt Baker:
5cm last 12h
15cm last 24h
******************
Mt Cain:
0cm last 12h
0cm last 24h
******************
```
```
Information
```
```
Here are the keywords you can use:
'update': you will receive the current status on the mountain.
'register': you will be registered for morning text if fresh snow on the local mountain.
'unregister': you will not receive morning texts anymore.
'information': lists all available keywords and their effect.
```
```
Register
```
```
You will now receive updates in the morning if it snows overnight
on the Vancouver local mountains.
You can stop it at any moment by sending 'unregister' to this number.
```
```
Unregister
```
```
You will stop receiving automatic updates. You can always reactivate the service by sending 'register'
```
```
sdlkfjbssadkljb
```
```
Sorry buddy, the only keywords accepted are 'update', 'register', 'unregister'.
If it's your first time using the app, send 'information' for more insight on the keywords effects.
```
