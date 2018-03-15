#! /usr/bin/env python

import pow_alert
from flask.json import jsonify
import json


def make():
    result = pow_alert.check_snow()
    with open('report.cache', 'w') as file:
        file.write(json.dumps(result, indent=4))


def get():
    try:
        with open('report.cache', 'r') as file:
            return json.load(file)
    except:
        return ''


if __name__ == "__main__":
    make()