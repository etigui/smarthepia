import requests
requests.packages.urllib3.disable_warnings()
from platform import system as system_name
from subprocess import call as system_call
import os
import subprocess

# Client SMTP
import smtplib
import email.message

# Local import
import const

# HTML mail
from html import database
from html import web_server


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
        if system_call(command, stdout=open(os.devnull, 'wb')) != 0:
            return False
    return True

# Get http request
def get_http(url):
    try:
        r = requests.get(url, timeout=3, verify=False)
        r.raise_for_status()
        return True
    except requests.exceptions.HTTPError as errh:
        if const.DEBUG: print("Http Error:", errh)
        return False
    except requests.exceptions.ConnectionError as errc:
        if const.DEBUG: print("Error Connecting:", errc)
        return False
    except requests.exceptions.Timeout as errt:
        if const.DEBUG: print("Timeout Error:", errt)
        return False
    except requests.exceptions.RequestException as err:
        if const.DEBUG: print("OOps: Something Else", err)
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
        r = requests.get(url, timeout=3, verify=False)
        return True, r.json()
    except requests.exceptions.HTTPError as errh:
        return False, None
    except requests.exceptions.ConnectionError as errc:
        return False, None
    except requests.exceptions.Timeout as errt:
        return False, None
    except requests.exceptions.RequestException as err:
        return False, None


# Send mail
def send_mail(email_from, email_to, password, message, subject):

    # Mail content
    msg = email.message.Message()
    msg['Subject'] = subject
    msg['From'] = email_from
    msg['To'] = email_to
    password = password
    msg.add_header('Content-Type', 'text/html')
    msg.set_payload(message)

    # Init client
    client = smtplib.SMTP('smtp.gmail.com: 587')
    client.starttls()

    # Login Credentials for sending the mail
    client.login(msg['From'], password)

    # Send and quit
    client.sendmail(msg['From'], [msg['To']], msg.as_string())
    client.quit()
    if const.DEBUG: print(f"successfully sent html to {msg['To']}")


# Send mail if the database is down
def send_database_alert(email_from, admin_email, password, subject):

    # Send email to all admin
    for email_to in admin_email:
        message = database.email_html_database(email_splitter(email_to))
        send_mail(email_from, email_to, password, message, subject)


# Send mail if the web server is down
def send_web_server_alert(email_from, email_to, password, subject):
    message = web_server.email_html_web_server(email_splitter(email_to))
    send_mail(email_from, email_to, password, message, subject)


# Notify server web when new alarm
# Then when the web server receive the request
# it send new alarm in the socket
def notify_alarm_change(url_get, notify_response):
    try:
        s = requests.Session()
        data = {"email": const.ws_notify_email, "password": const.ws_notify_password}
        s.post(const.ws_notify_url_post, data=data, verify=False)
        response = s.get(url_get, verify=False)
        if response.status_code == 200:
            if response.json() != notify_response:
                return True
            else:
                return False
        else:
            return False
    except requests.exceptions.HTTPError as errh:
        return False
    except requests.exceptions.ConnectionError as errc:
        return False
    except requests.exceptions.Timeout as errt:
        return False
    except requests.exceptions.RequestException as err:
        return False


    # Remove duplicate from list
def remove_duplicates(datas):
    output = []
    seen = set()
    for data in datas:
        # If value has not been encountered yet,
        # ... add it to both list and set.
        if data not in seen:
            output.append(data)
            seen.add(data)
    return output

# Get http request
def http_get_request_json(url):
    try:
        r = requests.get(url, timeout=3, verify=False)
        if r.status_code == 200:
            return True, r.json()
        else:
            return False, None
    except requests.exceptions.HTTPError as errh:
        return False, None
    except requests.exceptions.ConnectionError as errc:
        return False, None
    except requests.exceptions.Timeout as errt:
        return False, None
    except requests.exceptions.RequestException as err:
        return False, None
