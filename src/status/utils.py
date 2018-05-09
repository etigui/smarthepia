from platform import system as system_name
from subprocess import call as system_call
import urllib3
import os



"""
Returns True if host (str) responds to a ping request. Remember that a host may not respond to a ping (ICMP)
request even if the host name is valid.
"""
def send_ping(host):

    # Check OS type
    if system_name().lower() == 'windows':
        command = ['ping', '-n', '1', host]
    else:
        command = ['ping', '-c', '1', host]

    # Check if ping error (r==0=>ok;r==2=>no_reponse;else=>failed)
    if system_call(command, stdout=open(os.devnull, 'wb')) != 0:
        return False
    return True


def rest_server_status(url):
    http = urllib3.PoolManager()
    response = http.request('GET', url)
    if response.status == 200:
        return True
    else:
        return False

