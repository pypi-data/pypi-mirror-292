"""Module to hold generate functions."""

import fileinput
import os
import shutil

from .helper import plural, singular

model_datatypes = {'string':'String', 'text': 'Text', 'int':'Integer', 'float':'Float', 'decimal':'Numberic',
           'bool':'Boolean','date':'Date','time':'Time','datetime': 'DateTime', 'bytes':'LargeBinary','uuid':'UUID',
           'dict': 'JSON','json':'JSON','list':'ARRAY','array':'ARRAY','number':'Integer'}

view_datatypes = {'string':'text', 'text': 'text', 'int':'number', 'float':'number', 'decimal':'number',
           'bool':'Boolean','date':'date','time':'datetime-local','datetime': 'datetime-local', 'bytes':'file','number':'number'}

def generate_app(name):

    app_path = os.path.join(os.getcwd(),name)
    if os.path.exists(app_path):
        print('App already Exists')
        return

    os.makedirs(app_path)
    shutil.copytree(os.path.dirname(__file__) + '/template', app_path, dirs_exist_ok=True)
    print('App Created Successfully at {}'.format(app_path))
    return

def generate_controller(name):

    filepath = os.path.join(os.getcwd(),'controllers','{}.py'.format(name))

    if not os.path.exists(os.path.join(os.getcwd(),'controllers')):
        print('Creating controllers Directory')
        os.mkdir(os.path.join(os.getcwd(),'controllers'))

    print('creating file {}'.format(filepath))
    shutil.copy(os.path.join(os.path.dirname(__file__), 'sample','controller.txt'), filepath)
    with fileinput.input(filepath, inplace=True) as f:
        for line in f:
            modified_line = line.replace('controller', name).replace('url',plural(name))
            print(modified_line, end='')
    print('{} created successfully'.format(filepath))

    r_file = open(os.path.join(os.getcwd(),'app.py'), "a")
    r_file.write('controllers.append("{}")\n'.format(plural(name)))
    r_file.close()
    generate_routes(name)
    return

def generate_routes(name):
    route = 'from .controllers import {}\n'.format(name)
    filepath = os.path.join(os.getcwd(),'routes.py')

    routes = open(filepath,'r').readlines()
    if route in routes:
        print('Route already exists')
        return
    print('Adding routes for {}'.format(name))

    r_file = open(filepath, "a")
    r_file.write(route)
    r_file.close()

    return

def generate_helper(name):

    filepath = os.path.join(os.getcwd(),'helpers','{}.py'.format(name))

    if not os.path.exists(os.path.join(os.getcwd(),'helpers')):
        print('Creating helpers Directory')
        os.mkdir(os.path.join(os.getcwd(),'helpers'))

    print('creating file {}'.format(filepath))
    shutil.copy(os.path.join(os.path.dirname(__file__), 'sample','helper.txt'), filepath)
    with fileinput.input(filepath, inplace=True) as f:
        for line in f:
            modified_line = line.replace('from ..models.name import name as model ', 'from ..models.{} import {} as model '.format(name,name.capitalize()))
            print(modified_line, end='')
    print('{} created successfully'.format(filepath))

    return

def generate_model(name, args):

    if not os.path.exists(os.path.join(os.getcwd(),'models')):
        print('Creating models Directory')
        os.mkdir(os.path.join(os.getcwd(),'models'))

    model = []
    model.append('from sqlalchemy.types import *')
    model.append('from sqlalchemy.sql import func')
    model.append('from sqlalchemy import inspect')
    model.append('from ..database import db')
    model.append('import uuid')

    model.append("class {}(db.Model):".format(name.capitalize()))
    model.append("\n\t__tablename__ = '{}'\n".format(name))
    model.append("\tdef toDict(self):")
    model.append("\t\treturn { c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs }\n")
    model.append('\tid = db.Column(String, primary_key=True)')
    # model.append('\tid = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)')
    model.append('\tcreated = db.Column(DateTime, default=func.now(), nullable=False)')
    model.append('\tupdated = db.Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)')

    for arg in args:
        model.append("\t{} = db.Column({}, nullable=True)".format(arg.split(':')[0], model_datatypes[arg.split(':')[1]]))

    generate_file(os.path.join(os.getcwd(),'models'), name + '.py',model)
    return

def generate_html(name,args):

    if not os.path.exists(os.path.join(os.getcwd(),'templates')):
        print('Creating templates Directory')
        os.mkdir(os.path.join(os.getcwd(),'templates'))
        shutil.copytree(os.path.dirname(__file__) + '/template/templates', os.path.join(os.getcwd(),'templates'), dirs_exist_ok=True)
        shutil.copytree(os.path.dirname(__file__) + '/template/static', os.path.join(os.getcwd(),'templates'), dirs_exist_ok=True)


    html = []
    html.append("{% extends 'base.html' %}")
    html.append('{% block header %}')

    for arg in args:
        html.append('<th colspan="1" class="sort">{}</th>'.format(arg.split(':')[0].upper()))
    html.append('{% endblock %}\n')

    html.append('{% block inputs %}')
    for arg in args:
        html.append('<td colspan="1" class="{0}"><input id="{0}" type="{1}" placeholder="{0}"  /></td>'.format(arg.split(':')[0],view_datatypes[arg.split(':')[1]]))
    html.append('{% endblock %}\n')

    html.append('{% block data %}')
    html.append('{% for item in data %}')
    html.append('<tr id="{{item.id}}">')
    html.append('<td colspan="1"><i class="edit fa fa-pencil" aria-hidden="true"></i></td>')
    html.append('<td colspan="1"><i class="remove fa fa-trash" aria-hidden="true"></i></td>')

    for arg in args:
        html.append('<td colspan="1" class="{0}">{1}item.{0}{2}</td>'.format(arg.split(':')[0], '{{','}}'))


    html.append('</tr>\n{% endfor %}')
    html.append('{% endblock %}')

    generate_file(os.path.join(os.getcwd(),'templates'), plural(name) + '.html',html)
    return

def generate_file(filepath, filename,code):
    # create the file
    if not os.path.exists(filepath):
        os.makedirs(filepath)

    print('creating file {}'.format(os.path.join(filepath,filename)))
    with open(os.path.join(filepath,filename), 'w') as f:
        for line in code:
            f.write(f'{line}\n')
    f.close()
    print('{} created successfully'.format(os.path.join(filepath,filename)))

def generate_code(args):
    name = singular(args[1])

    if args[0] == "app":
        generate_app(name)

    elif args[0] == 'model':
        generate_model(name, args[2:])

    elif args[0] == 'view':
        generate_html(name,args[2:])

    elif args[0] == 'helper':
        generate_helper(name)

    elif args[0] == 'controller':
        if not os.path.exists(os.path.join(os.getcwd(),'models','{}.py'.format(name))):
            generate_model(name, args[2:])
        if not os.path.exists(os.path.join(os.getcwd(),'helpers','{}.py'.format(name))):
            generate_helper(name)
        generate_controller(name)
        return

    elif args[0] == 'scaffold':
        if not os.path.exists(os.path.join(os.getcwd(),'models','{}.py'.format(name))):
            generate_model(name, args[2:])
        if not os.path.exists(os.path.join(os.getcwd(),'helpers','{}.py'.format(name))):
            generate_helper(name)
        generate_controller(name)
        generate_html(name,args[2:])
        return




