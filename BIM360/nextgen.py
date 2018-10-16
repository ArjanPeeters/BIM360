import requests
import json
import config
import time
import pprint as pp


def _url(path):
    """
    Defines the base url
    """

    account_id = config.account_details['account_id']

    if path[:1] == "/":
        c_path = path[1:]
    else:
        c_path = path

    if config.SETTINGS['server'] == 'eu':
        url = "https://developer.api.autodesk.com/hq/v1/regions/eu/accounts/{0}/{1}".format(account_id, c_path)
        print('command:', url)
        return url

    else:
        url = "https://developer.api.autodesk.com/hq/v1/accounts/{0}}".format(account_id, c_path)
        print('command:', url)
        return url


def __login():
    """
    Response
    HTTP Status Code Summary
    200  OK  Successful request; access token returned.
    400  Bad Request  One or more parameters are invalid. Examine the response payload body for details.
    401  Unauthorized  The client_id and client_secret combination is not valid.
    403  Forbidden  The client_id is not authorized to access this endpoint.
    415  Unsupported Media Type  The Content-Type header is missing or specifies a value other than application/x-www-form-urlencoded.
    429  Too Many Requests  Rate limit exceeded; wait some time before retrying.
    500  Internal Server Error  Generic internal server error.
    Response
    Body Structure (200)
    The response body for a successful call is a flat JSON object with the following attributes:

    token_type
    string
    Will always be Bearer
    expires_in
    int
    Access token expiration time (in seconds)
    access_token
    string
    The access token
    """

    url = "https://developer.api.autodesk.com/authentication/v1/authenticate"

    data = {
        "client_id": config.account_details['client_id'],
        "client_secret": config.account_details['client_secret'],
        "Account_id": config.account_details['account_id'],
        'scope': "data:read account:read bucket:read",
        'grant_type': 'client_credentials'
    }

    headers = {
        'Content-Type': "application/x-www-form-urlencoded",
        'Cache-Control': "no-cache"
    }

    response = requests.post(url, data, headers)

    if response.status_code != 200:
        raise NotImplementedError(response.status_code, response.json())

    else:
        token = response.json()['access_token']

        config.SETTINGS['forge_token'] = token
        config.SETTINGS['sec_epoch'] = time.time() + response.json()[
            'expires_in']
        print('expires on', config.SETTINGS['sec_epoch'],'in sec:',response.json()['expires_in'], "epoch now:", time.time(), 'Forge token:', token)
        return token


def get_token():
    '''
    function for checking if already logged in. else login
    '''

    if config.SETTINGS.__contains__('forge_token'):
        """
        if settings contains a forge token, check if expired. If expired login else use token
        """

        if config.SETTINGS['sec_epoch'] < time.time():
            # check if time is expired, if so login again
            print('expired:', config.SETTINGS['sec_epoch'], 'epoch now:' ,time.time())
            return __login()

        else:
            return config.SETTINGS['forge_token']

    else:
        return __login()


def command(rtype, path, **parameters):

    """
    Request
    Query String Parameters
    limit  int  Response array’s size  Default value: 10  Max limit: 100
    offset  int  Offset of response array  Default value: 0
    sort  string  Comma-separated fields to sort by in ascending order

    Prepending a field with - sorts in descending order
    Invalid fields and whitespaces will be ignored
    field  string  Comma-separated fields to include in response

    id will always be returned
    Invalid fields will be ignored
    Response
    HTTP Status Code Summary
    200  OK  The request has succeeded.
    400  Bad Request  The request could not be understood by the server due to malformed syntax.
    403  Forbidden  Unauthorized
    404  Not Found  The resource cannot be found.
    409  Conflict  The request could not be completed due to a conflict with the current state of the resource.
    422  Unprocessable Entity  The request was unable to be followed due to restrictions.
    500  Internal Server Error  An unexpected error occurred on the server.
    """
    url = _url(path)
    headers = {}
    data = {}
    headers['Authorization'] = 'Bearer {}'.format(get_token())
    headers['Content-Type'] = 'application/json'
    headers['scope'] = parameters.pop('scope','account:read')
    data['grand_type'] = 'client_credentials'
    data['limit'] = parameters.pop('limit',10)
    data['offset'] = parameters.pop('offset',0)
    record_count = data['limit']
    for key, value in parameters.items():
      data[key] = value

    all_records = []
    crt = 0
    while data['limit'] == record_count:
        response = requests.request(rtype,url,headers=headers,params=data)
        if response.status_code != 200:
            raise NotImplementedError(response.status_code, response.json())
        elif len(response.json()) == 0:
            print('no records',response.json())
            record_count == -1
        else:
            all_records.append(response.json())
            data['offset'] += data['limit']
            record_count = len(response.json())
            crt += record_count
        print(response.status_code, rtype, path, 'offset:', data['offset'], 'limit:', data['limit'], 'records:',record_count)

    if len(all_records) > 1:
        flat_records = [item for sublist in all_records for item in sublist]
        print('returned {} records'.format(crt))
        return flat_records
    else:
        return all_records

def list_of_project_parameters(*parameters):
    """
    retrieve a list of a specified projects parameter
    """

    response = command("GET","projects")

    list_of_parameters = []

    if len(parameters) > 1:

        for i in range(len(response)):
            dict = {}

            for p in parameters:
                dict[p] = response[i][p]
            list_of_parameters.append(dict)
        print("Parameters", parameters, "found in", len(list_of_parameters), "projects found")

    else:
        for i in response:
            list_of_parameters.append(i[parameters[0]])
        print("Parameter", parameters, "found in", len(list_of_parameters), "projects found")

    return list_of_parameters


def list_of_project_names():
    """
    retrieve a list of projects names
    """

    return list_of_project_parameters('name')

def list_of_project_ids():
    """
    retrieve a list of projects ids
    """

    return list_of_project_parameters('id')

def get_project_id_with_project_name(name):
    """
    Find a project id with the name of the project
    """

    projects_list = list_of_project_parameters('name','id')

    search_list = {}

    for i in projects_list:
        search_list[i['name'].lower()] = i['id']

    if name.lower() in search_list:
        print('Project:', name, ' id:', search_list[name.lower()])
        return search_list[name.lower()]
    else:
        print('Project:', name, 'not found')
        return "not found"

def get_projects_of_servicetype(*stype):
    """
    Return all projects with type of services
    """
    project_ids = list_of_project_ids()
    projects_with_servicetypes = []
    service_types_with_projects = {}

    for id in project_ids:
        all_project_info = command('get', 'projects/{}'.format(id))[0]
        projects_with_servicetypes.append(
            {
                'name': all_project_info['name'],
                'id': id,
                'service_types': all_project_info['service_types'].split(",")
            }
        )
        for st in all_project_info['service_types'].split(","):
            d = {all_project_info['name']: id}
            if st in service_types_with_projects:
                service_types_with_projects[st].append(d)
            else:
                service_types_with_projects[st] = [d]

    if stype[0] == "all":
        return service_types_with_projects
    elif len(stype) == 1:
        try:
            return service_types_with_projects[stype[0]]
        except KeyError:
            return "Service Type: {} does not exist".format(stype[0])
    else:
        list = {}
        for s in stype:
            try:
                list[s] = (service_types_with_projects[s])
            except KeyError:
                list[s] = "Service Type {} does not exist".format(s)
        return list