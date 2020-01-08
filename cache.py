#! /usr/bin/env python

import os
import pow_alert
from flask.json import jsonify
import json
from logger import *

curr_dir = os.path.dirname(os.path.realpath(__file__))
cacheFile = f"{curr_dir}/report.cache"

def make():
    result = pow_alert.check_snow()
    with open(f"{cacheFile}", 'w') as file:
        json_str = json.dumps(result, indent=4)

        log.debug(f"Dump snow report in {cacheFile}:\n {json_str}")
        file.write(json_str)


def get():
    try:
        with open(f"{curr_dir}/report.cache", 'r') as file:
            cache_json = json.load(file)
            log.debug(f"Retrieve snow report from cache file: \n{cache_json}")
            return cache_json
    except:
        return ''


if __name__ == "__main__":
    make()
