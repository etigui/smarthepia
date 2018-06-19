import requests
from platform import system as system_name
from subprocess import call as system_call
import os
import subprocess



import const


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


# Get http request
def request_api(url):
    try:
        r = requests.get(url, timeout=3)
        return True, r.json()
    except requests.exceptions.HTTPError as errh:
        return False, None
    except requests.exceptions.ConnectionError as errc:
        return False, None
    except requests.exceptions.Timeout as errt:
        return False, None
    except requests.exceptions.RequestException as err:
        return False, None

# Get current weather
def get_current_weather():

    # Check if the API return good value
    status, json = request_api(const.route_current_weather())
    if json['cod'] == const.return_code_success:
        if status:
            return True, json
        else:
            return False, None
    else:
        return False, None

# Get forecast (5 days every 3h)
def get_forecast():

    # Check if the API return good value
    status, json = request_api(const.route_forecast())
    if json['cod'] == const.return_code_success:
        if status:
            return True, json
        else:
            return False, None
    else:
        return False, None


def get_degree_from_fahrenheit(fahrenheit):
    return (fahrenheit - 32) / 1.8


