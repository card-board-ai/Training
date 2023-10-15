from supabase.client import Client, create_client
from simple_term_menu import TerminalMenu
from inspect import isfunction
import configparser
import importlib
import inspect


config = configparser.ConfigParser()
config.read('keys.cfg')

environment = input("Which environment are we training, local or prod?: ")
if environment == "local":
    supa_key = config.get('Supabase', 'local_key')
    supa_client: Client = create_client(config.get('Supabase', 'local_url'),
                                        supa_key)
elif environment == "prod":
    supa_key = config.get('Supabase', 'prod_private_key')
    supa_client: Client = create_client(config.get('Supabase', 'prod_url'),
                                        supa_key)
else:
    raise Exception("That is not an available environment")


# grab the file names from the db
games = supa_client.table('games').select("training_file").execute()
menu_options = ["Select All"]
functions = []


# this iterates through the provided fil names from db and creates lists for the menu and function execution
for item in games.data:
    file = item.get('training_file')
    module = importlib.import_module(file)
    # based on https://stackoverflow.com/questions/66084762/call-function-from-another-file-without-import-clause
    for attribute_name in dir(module):
        attribute = getattr(module, attribute_name)
        if isfunction(attribute) and not attribute_name.startswith("_"):
            menu_options.append(attribute.__name__)
            functions.append(attribute)

# display cli menu
terminal_menu = TerminalMenu(
    menu_options,
    title='',
    multi_select=True,
    show_multi_select_hint=True,)
choice_index = terminal_menu.show()


def build_args(function):
    signature = inspect.signature(function)
    parameters = signature.parameters
    func_args = {}
    for param in parameters:
        if param == "supa_client":
            func_args.update({param: supa_client})
        elif param == "supa_key":
            func_args.update({param: supa_key})
        elif param == "config":
            func_args.update({param: config})
    return func_args


"""
if the choice includes 'Select All' then execute all
available functions otherwise iterate through fireing the chossen functions
"""
if choice_index[0] == 0:
    for item in functions:
        args = build_args(item)
        item(**args)
else:
    for item in choice_index:
        args = build_args(functions[item - 1])
        functions[item - 1](**args)
