#! /usr/bin/env python

import pow_alert
from flask.json import jsonify
import json


def create_cache():
    result = pow_alert.check_snow()
    with open('report.cache', 'w') as file:
        file.write(json.dumps(result, indent=4))


def get_cache():
    try:
        with open('report.cache', 'r') as file:
            return json.load(file)
    except:
        return ''


if __name__ == "__main__":
    create_cache()
