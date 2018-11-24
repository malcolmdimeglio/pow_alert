#! /usr/bin/env python

import os
import pow_alert
from flask.json import jsonify
import json

curr_dir = os.path.dirname(os.path.realpath(__file__))

def make():
    result = pow_alert.check_snow()
    with open(f"{curr_dir}/report.cache", 'w') as file:
        file.write(json.dumps(result, indent=4))


def get():
    try:
        with open(f"{curr_dir}/report.cache", 'r') as file:
            return json.load(file)
    except:
        return ''


if __name__ == "__main__":
    make()
