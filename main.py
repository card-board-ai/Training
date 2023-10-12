import configparser
import importlib
from inspect import isfunction
from supabase.client import Client, create_client
from simple_term_menu import TerminalMenu

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

games = supa_client.table('games').select("training_file").execute()
menu_options = ["Select All"]
functions = []

for item in games.data:
    file = item.get('training_file')
    module = importlib.import_module(file)
    # based on https://stackoverflow.com/questions/66084762/call-function-from-another-file-without-import-clause
    for attribute_name in dir(module):
        attribute = getattr(module, attribute_name)
        if isfunction(attribute) and not attribute_name.startswith("_"):
            menu_options.append(attribute.__name__)
            functions.append(attribute)

terminal_menu = TerminalMenu(
    menu_options,
    title='',
    multi_select=True,
    show_multi_select_hint=True,)
choice_index = terminal_menu.show()
print(choice_index)
print(terminal_menu.chosen_menu_entries)
print(functions)

if choice_index[0] == 0:
    for item in functions:
        item()
else:
    for item in choice_index:
        functions[item - 1]()
