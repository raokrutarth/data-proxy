import os
import requests

# script to publish home-server IP address to protected data proxy queue.

def check_in():
    fqn = os.uname().nodename
    ext_ip = requests.get('https://api.ipify.org?format=json').json()
    # https://www.ipify.org/
    print("Asset: {}. Checking in from IP#: {} ".format(fqn, ext_ip))

check_in()