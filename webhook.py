#! /usr/bin/env python


from pow_alert import check_snow, pretify_data
import SQLitedb as sql
from flask import Flask, request
from flask_cors import CORS
from flask.json import jsonify
import notifications
import json
import subprocess
import os

app = Flask(__name__)
CORS(app)


def update(to_num):
    result = check_snow()
    txt_message = pretify_data(result)
    notifications.send_sms(txt_message, to_num)

@app.route('/')
def handler():
    msg = request.args['Body'].lower().strip()
    client_num = request.args['From']
    # when using notifications.send_sms() method, remember that From and To args received are reversed when message sent

    sql.update_database(client_num, msg)

    if msg.lower().strip() == "update":
        update(client_num)
    elif msg == "register":
        txt = f"You will now receive updates in the morning if it snows overnight " \
              f"on the Vancouver local mountains.\n" \
              f"You can stop it at any moment by sending 'unregister' to this number."
        notifications.send_sms(txt, client_num)
    elif msg == "unregister":
        txt = f"You will stop receiving automatic updates. You can always reactivate the service by sending 'register'."
        notifications.send_sms(txt, client_num)
    elif msg == "remove":
        txt = f"Your phone number has been successfully removed from the database."
        notifications.send_sms(txt, client_num)
    elif msg == "information":
        txt = f"Here are the keywords you can use:\n" \
               "'update': you will receive the current status on the mountain.\n\n" \
               "'register': you will be registered for morning texts if fresh snow on the local mountain.\n\n" \
               "'unregister': you will not receive morning texts anymore.\n\n" \
               "'information': lists all available keywords and their effect."
        notifications.send_sms(txt, client_num)
    else:
        txt = f"Sorry buddy, the only keywords accepted are 'update', 'register' and 'unregister'.\n" \
               "If it's your first time using the app, send 'information' for more insight on the keywords effects."
        notifications.send_sms(txt, client_num)

    return ''  # Flask needs a return str

@app.route('/json')
def index():
    result = check_snow()
    return jsonify(result)

@app.route('/github', methods=['POST'])
def github_hook():
    event = request.headers.get('X-GitHub-Event')
    payload = json.loads(request.data)
    with open('log/githubHook.log','w') as file:
        file.write(f"X-GitHub-Event = {event}\n{json.dumps(payload, indent=4)}")

    if event == 'ping':
        return 'pong'

    if event == 'push':
        subprocess.check_call(['/usr/bin/git', 'pull'], shell=False)

        # NOTE: It looks like using a subprocess doesn't work for the following command. Either with shell True or False
        # THOUGHT: restarting the main process with its own subprocess is not a good idea.
        # it's seems like trying to bite the hand that feeds you
        # os.system seems to use external process to restart the service and seems to be out of the main service scope.
        # Being free of any service process os.system can thus restart one.
        # To be confirmed!
        os.system("service pow_alert restart")
    return 'Repository pulled'


if __name__ == "__main__":
    app.run()


