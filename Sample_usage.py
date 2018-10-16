from BIM360 import nextgen as ng
from BIM360 import classic as cl

'''
sample usages of next-gen / hq projects
'''

#commands login them selves, but you could use ng.__login()

#retreve a list of all project id's
project_ids = ng.list_of_project_ids()

#retreve a list of all project names
project_names = ng.list_of_project_names()

#get a project id by project name
just_one_id = ng.get_project_id_with_project_name(project_names[0])

#get multiple project parameters
multiple_parameters = ng.list_of_project_parameters('id', 'name', 'start_date', 'end_date')

#use different commands from forge
command_return = ng.command('get','projects/{}'.format(just_one_id))

#get different service types and corresponding projects
#you can give the name of one or multiple types (seperated with a comma) or simply use 'all
service_types = ng.get_projects_of_servicetype('all')

print('Total number of projects is:', len(project_ids))
print('Project ids:', project_ids[0:5])
print('Project Names:', project_names[0:5])
print('Id of', project_names[0], 'is', just_one_id)
print('Multiple project parameters:', multiple_parameters[0:5])
print('Command: project/{} is:'.format(just_one_id),command_return)
print('all service types:')
print(service_types)

'''
sample usage of classic field
'''

#get all id's from projects in classic field
field_ids = cl.list_of_project_ids()

#get all names from projects in classic field
field_names = cl.list_of_project_names()

#get the id of a project name
field_id_by_name = cl.get_project_id_with_project_name(field_names[0])

#use a different command documentend in the api
#see https://bim360field.autodesk.com/apidoc/index.html#mobile_api
classic_command = cl.command('post', 'api/project', project_id=field_id_by_name)

print('Total number of classic field projects is:', len(field_ids))
print('project ids:', field_ids[0:5])
print('project names:', field_names[0:5])
print('Id of', field_names[0], 'is', field_id_by_name)
print('Command POST api/project is:', classic_command)