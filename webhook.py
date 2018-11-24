#! /usr/bin/env python


from pow_alert import check_snow, prettify_data
import cache
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

curr_dir = os.path.dirname(os.path.realpath(__file__))

# This entry point is ran only if 'update' is called(texted) by any number
def update(to_num):
    cache_resorts_list = cache.get()
    txt_message = prettify_data(cache_resorts_list)
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
               "'update': you will receive the current status on all available mountains.\n\n" \
               "'register': you will be registered for morning texts only if there is fresh snow on the local mountains.\n\n" \
               "'unregister': you will not receive morning texts anymore.\n\n" \
               "'information': lists all available keywords and their effect."
        notifications.send_sms(txt, client_num)
    else:
        txt = f"Sorry buddy, the only keywords accepted are 'update', 'register' and 'unregister'.\n" \
               "If it's your first time using the app, send 'information'."
        notifications.send_sms(txt, client_num)

    return ''  # Flask needs a return str

@app.route('/json')
def json_info():
    result = check_snow()
    return jsonify(result)

@app.route('/github', methods=['POST'])
def github_hook():
    event = request.headers.get('X-GitHub-Event')
    payload = json.loads(request.data)
    with open(f"{curr_dir}/log/githubHook.log",'w') as file:
        file.write(f"X-GitHub-Event = {event}\n{json.dumps(payload, indent=4)}")

    if event == 'ping':
        return 'pong'

    if event == 'push':
        subprocess.check_call(['/usr/bin/git', 'pull'], shell=False)

        # NOTE: subprocess.check_call(['/bin/systemctl', 'restart', 'pow_alert'], shell=False)
        # and subprocess.check_call(['/bin/systemctl restart pow_alert'], shell=True) work too.
        # Meaning the process is properly restarted
        # Although both of them raise an error :
        # subprocess.CalledProcessError Command '['/bin/systemctl restart pow_alert']' died with <Signals.SIGTERM: 15>
        # Since systemctl sends a SIGTERM signal to restart the process that is running this script, an error is raised
        # metaphorically it's like trying to bite the hand that feeds you
        # This could be solved with a try:except command
        # Which one is better?
        #
        # try:
        #     subprocess.check_call(['/bin/systemctl', 'restart', 'pow_alert'], shell=False)
        # except subprocess.CalledProcessError:
        #     pass

        os.system("/bin/systemctl restart pow_alert")
        cache.make()
    return 'Repository pulled'


@app.route('/index')
def index():
    return "<h1 style='color:blue'>Hello There!</h1>"


if __name__ == "__main__":
    app.run()


