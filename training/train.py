from training.train_games.train_game import TrainGame
from inspect import isfunction, ismethod, isclass
from simple_term_menu import TerminalMenu
import importlib
import inspect
import os

        # def get_class_args(cls):
        #     # Get the signature of the class's __init__ method
        #   init_signature = inspect.signature(cls.__init__)
        #   args = []
        # 
        # # Iterate over the parameters in the signature, skipping 'self'
        # for name, parameter in init_signature.parameters.items():
        #     if name == "self":
        #         continue
        #     if parameter.default is inspect.Parameter.empty:
        #         args.append(name)  # Required argument
        #     else:
        #         args.append(f"{name}={parameter.default}")  # Optional argument with default value
        # 
        # return args
        
        
def traindbs(games, config, supa_key, supa_client):
    menu_options = ["Select All"]
    functions = []
    
    def build_args(nme):
        # If the callable object is a class, focus on its __init__ method.
        # Exclude built-in classes for which inspect.signature might fail.
        if inspect.isclass(nme) and not nme.__name__ in dir(__builtins__):
            func = nme.__init__
        else:
            func = nme

        # Get the signature of the function or class __init__ method
        try:
            signature = inspect.signature(func)
        except ValueError:
            return [], []  # In case of built-in functions/classes with no inspectable signature

        required_args = {}

        # Iterate over the parameters in the signature
        for name, parameter in signature.parameters.items():
            if name == "self":
                continue  # Skip 'self' for methods
            if parameter.default is inspect.Parameter.empty:
                if parameter == "supa_client":
                    required_args.update({parameter: supa_client})
                elif parameter == "supa_key":
                    required_args.update({parameter: supa_key})
                elif parameter == "config":
                    required_args.update({parameter: config})
                elif parameter == "games":
                    required_args.update({parameter: games})

        return required_args
    
    # this iterates through the provided file names from db and creates lists for the menu and function execution
    for item in games.data:
        file_name = item.get('training_file')
        if os.path.exists(f"training/train_games/{file_name}.py"):
            module = importlib.import_module(f".train_games.{file_name}", "training")
            module_name = module.__name__
            class_args = build_args(TrainGame)
            # based https://stackoverflow.com/questions/66084762/call-function-from-another-file-without-import-clause
            
            for attribute_name in dir(module):
                attribute = getattr(module, attribute_name)
                if isfunction(attribute) and attribute.__module__ == module_name and not attribute_name.startswith("_"):
                    menu_options.append(attribute.__name__)
                    functions.append(attribute)
                elif isclass(attribute) and attribute.__module__ == module_name:
                    try:
                        print(attribute)
                        instance = attribute(**build_args(attribute))  # This works if the class has a no-argument constructor
                    except TypeError:
                        print(f"Skipping {attribute.__name__} due to constructor arguments.")
                        continue
                    # Iterate through all attributes of the instance
                    for class_attr_name in dir(instance):
                        class_attr = getattr(instance, class_attr_name)
                        # Check if the attribute of the instance is a function/method
                        if isfunction(class_attr) or ismethod(class_attr):
                            if not class_attr_name.startswith("_"):  # Filter out 'private' methods
                                func_name = f"{attribute.__name__}.{class_attr_name}"
                                menu_options.append(func_name)
                                # Store the bound method from the instance
                                functions.append(getattr(instance, class_attr_name))

    # display cli menu
    function_menu = TerminalMenu(
        menu_options,
        title='',
        multi_select=True,
        show_multi_select_hint=True, )
    choice_index = function_menu.show()

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
