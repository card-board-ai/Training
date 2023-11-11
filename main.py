from supabase.client import Client, create_client
from simple_term_menu import TerminalMenu
from rich.console import Console
import configparser
from train import traindbs
from new_game import create_game

console = Console()

config = configparser.ConfigParser()
config.read('keys.cfg')

console.print("Which environment are we training?", style="bold green")
menu_options = ["Prod", "Local"]  # these are used to pull keys from keys file. update postgres headers if changed
terminal_menu = TerminalMenu(menu_options)
env_choice = terminal_menu.show()

environment = menu_options[env_choice]
if menu_options[env_choice] == "Local":
    supa_key = config.get('Supabase', 'local_key')
    supa_client: Client = create_client(config.get('Supabase', 'local_url'),
                                        supa_key)
elif menu_options[env_choice] == "Prod":
    supa_key = config.get('Supabase', 'prod_private_key')
    supa_client: Client = create_client(config.get('Supabase', 'prod_url'),
                                        supa_key)
else:
    raise Exception("That is not an available environment")

games = supa_client.table('games').select("*").execute()

action_options = ["Create new game", "Train"]
action_menu = TerminalMenu(action_options)
action_index = action_menu.show()
match action_index:
    case 0:  # creat new game
        create_game(games, supa_client, environment, config)
    case 1:  # train
        traindbs(games, config, supa_key, supa_client)
