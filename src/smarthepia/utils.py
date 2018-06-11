import requests


# Append dict item in list if not exist
def append_dependency_to_list(cursor):
    dependencies = []
    dependencies_set = set()
    for item in cursor:
        if item['dependency'] not in dependencies_set:
            dependencies.append(item['dependency'])
            dependencies_set.add(item['dependency'])
    return dependencies


# Split email to get only username
def email_splitter(email):
    return email.split('@')[0]
    # domain = email.split('@')[1]
    # domain_name = domain.split('.')[0]
    # domain_type = domain.split('.')[1]
    # print('Username : ', username)
    # print('Domain   : ', domain_name)
    # print('Type     : ', domain_type)


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
