import requests
from platform import system as system_name
from subprocess import call as system_call
import os

import subprocess


# Split email to get only username
def email_splitter(email):
    return email.split('@')[0]
    # domain = email.split('@')[1]
    # domain_name = domain.split('.')[0]
    # domain_type = domain.split('.')[1]
    # print('Username : ', username)
    # print('Domain   : ', domain_name)
    # print('Type     : ', domain_type)


"""
Returns True if host (str) responds to a ping request. Remember that a host may not respond to a ping (ICMP)
request even if the host name is valid.
"""
def send_ping(host):
    if system_name().lower() == 'windows':
        # command = ['ping', '-n', '1', host]
        if not send_ping_win(host):
            return False
    else:

        # Check if ping error (r==0=>ok;r==2=>no_reponse;else=>failed)
        command = ['ping', '-c', '1', host]
        if not system_call(command, stdout=open(os.devnull, 'wb')) != 0:
            return False
    return True
    '''
    # Check OS type
    if system_name().lower() == 'windows':
        send_ping_win(host)
        #command = ['ping', '-n', '1', host]
    else:
        command = ['ping', '-c', '1', host]

    # Check if ping error (r==0=>ok;r==2=>no_reponse;else=>failed)
    if system_call(command, stdout=open(os.devnull, 'wb')) != 0:
        return False
    return True
    '''


# Get http request
def get_http(url):
    try:
        r = requests.get(url, timeout=3)
        r.raise_for_status()
        return True
    except requests.exceptions.HTTPError as errh:
        print("Http Error:", errh)
        return False
    except requests.exceptions.ConnectionError as errc:
        print("Error Connecting:", errc)
        return False
    except requests.exceptions.Timeout as errt:
        print("Timeout Error:", errt)
        return False
    except requests.exceptions.RequestException as err:
        print("OOps: Something Else", err)
        return False


def send_ping_win(ip):
    status = subprocess.Popen('ping {0}'.format(ip), shell = True, universal_newlines = True, stdout = subprocess.PIPE).communicate()[0]
    #status = pingret.wait()
    if not ('unreachable' in status) and not ('Request timed out' in status):
        return True
    return False


# Add unique value to a list
def add_one_time_value_in_list(datas, index):
    list = []
    list_set = set()
    for item in datas:
        if item[index] not in list_set:
            list.append(item[index])
            list_set.add(item[index])
    return list
