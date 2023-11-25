from simple_term_menu import TerminalMenu
from inspect import isfunction
import importlib
import inspect
import os


def traindbs(games, config, supa_key, supa_client):
    menu_options = ["Select All"]
    functions = []
    
    # this iterates through the provided file names from db and creates lists for the menu and function execution
    for item in games.data:
        if os.path.exists(f"./{item.get('training_file')}.py"):
            file = item.get('training_file')
            module = importlib.import_module(file)
            # based https://stackoverflow.com/questions/66084762/call-function-from-another-file-without-import-clause
            for attribute_name in dir(module):
                attribute = getattr(module, attribute_name)
                if isfunction(attribute) and not attribute_name.startswith("_"):
                    menu_options.append(attribute.__name__)
                    functions.append(attribute)
    
    # display cli menu
    function_menu = TerminalMenu(
        menu_options,
        title='',
        multi_select=True,
        show_multi_select_hint=True,)
    choice_index = function_menu.show()
    
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
            