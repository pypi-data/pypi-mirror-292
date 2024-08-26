"""Module to hold destroy functions."""
import fileinput
import os

from .helper import plural, singular


def destroy_controller(name):
    name =singular(name)
    with fileinput.input(os.path.join(os.getcwd(),'routes.py'), inplace=True) as f:
        for line in f:
            modified_line = line.replace('from .controllers import {}'.format(name), '')
            print(modified_line, end='')

    if os.path.exists(os.path.join(os.getcwd(),'controllers','{}.py'.format(name))):
        os.remove(os.path.join(os.getcwd(),'controllers','{}.py'.format(name)))
    return

def destroy_helper(name):
    name =singular(name)
    if os.path.exists(os.path.join(os.getcwd(),'helpers','{}.py'.format(name))):
        os.remove(os.path.join(os.getcwd(),'helpers','{}.py'.format(name)))
    return

def destroy_model(name):
    name =singular(name)
    if os.path.exists(os.path.join(os.getcwd(),'models','{}.py'.format(name))):
        os.remove(os.path.join(os.getcwd(),'models','{}.py'.format(name)))
    return

def destroy_html(name):
    name =plural(name)
    if os.path.exists(os.path.join(os.getcwd(),'templates','{}.html'.format(name))):
        os.remove(os.path.join(os.getcwd(),'templates','{}.html'.format(name)))
    return

def destroy_code(type,name):

    if type == 'model':
        destroy_model(name)

    elif type == 'view':
        destroy_html(name)

    elif type == 'helper':
        destroy_helper(name)

    elif type == 'controller':
        destroy_controller(name)

    elif type == 'scaffold':
        destroy_controller(name)
        destroy_helper(name)
        destroy_model(name)
        destroy_html(name)

        return




