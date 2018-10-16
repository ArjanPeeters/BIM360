import requests
import json
import config


# defines base url for EU or US server
def _url(path):
    """
    Defines the base url
    """

    if path[:1] == "/":
        c_path = path[1:]

    else:
        c_path = path

    if config.SETTINGS['server'] == 'eu':
        url = "https://bim360field.eu.autodesk.com/{}".format(c_path)
        print('command:', url)
        return url

    else:
        url = "https://bim360field.autodesk.com/{}".format(c_path)
        print('command:', url)
        return url


# login to classic field
def __login(**device):
    """ POST /api/login

    Description: Attempts to authenticate with the mobile API using BIM 360 Field credentials. On success, returns a 36 byte GUID "ticket" which needs to be passed in on subsequent calls.

    Status Codes:
    200 User has authenticated and is successfully logged in.
    401 The user's credentials have been rejected.
    426 The user is a subcontractor on their active project, and login has been denied.
    Access: FREE
    Return: JSON - Returns a ticket which must be passed for each subsequent request in the session.

    Parameters:
        username : string - The username to authenticate as.
        password : string - The password to authenticate with.
        device_type : string - (optional) The type of device
        device_identifier : string - (optional) A unique identifier for the device.

    """

    data = {
        "username": config.user_details['username'],
        "password": config.user_details['password']
    }

    url = _url('api/login')

    response = requests.post(url, data)

    if response.status_code != 200:
        raise NotImplementedError(response.status_code, response.json())

    else:
        token = response.json()['ticket']
        config.SETTINGS['classic_token'] = token
        print("Field token: ", token)
        return token


def get_token():
    """
    If a token is available in config take that or else login to FIELD
    """

    if not config.SETTINGS.__contains__('classic_token'):
        print('logging in with', config.user_details['username'])
        token = __login()

    else:
        token = config.SETTINGS['classic_token']

    return token


def command(rtype, path, **parameters):
    """
    a general handler for BIM360 FIELD commands
    see documentation on: https://bim360field.autodesk.com/apidoc/index.html
    """

    url = _url(path)

    parameters['ticket'] = get_token()

    response = requests.request(rtype, url, data=parameters)

    if response.status_code != 200:
        raise NotImplementedError(response.status_code, response.json())

    else:
        return response.json()


def list_of_project_ids():
    """
    just retreve a list of all project_ids that user is involved in
    """

    response = command('POST', 'api/projects')

    list_of_ids = []
    print("Id's for", len(response), "projects found")

    for i in response:
        list_of_ids.append(i['project_id'])

    return list_of_ids


def list_of_project_names():
    """
    just retreve a list of all project names that user is involved in
    """

    response = command('POST', 'api/projects')

    list_of_names = []
    print("Names of", len(response), "projects found")

    for i in response:
        list_of_names.append(i['name'])

    return list_of_names


def get_project_id_with_project_name(name):
    """
    Function to find the project id with a given project name
    """

    response = command('POST', 'api/projects')

    list_names_ids = {}

    for i in response:
        list_names_ids[i['name'].lower()] = i['project_id']

    if name.lower() in list_names_ids:
        print('Project:', name, ', id:', list_names_ids[name.lower()])
        return list_names_ids[name.lower()]

    else:
        print("Project:", name, "not found")





