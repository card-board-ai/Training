from simple_term_menu import TerminalMenu
import psycopg2


def create_game(games_table, supa_client):
    games = []
    for item in games_table.data:
        name = item.get('game')
        games.append(name.casefold())
    
    # define the names of all required fields
    new_game_name: str = ""
    while new_game_name == "" or new_game_name.casefold() in games:
        new_game_name = input("New Game Name")
        if new_game_name.casefold() in games:
            print("That game alreday exists")
            
    new_rules_db = new_game_name.casefold().replace(" ", "_") + "_rules"
    new_rules_sq_function_name = "match_" + new_rules_db
    new_rules_kw_function_name = "kw_match_" + new_rules_db
    
    pieces_options = ["No", "Yes"]
    pieces_menu = TerminalMenu(
        pieces_options,
        title="Does this game need a pieces db?"
    )
    pieces_index = pieces_menu.show()
    match pieces_index:
        case 1:
            new_pieces_db = new_game_name.casefold().replace(" ", "_") + "pieces"
            new_pieces_sq_function_name = "match_" + new_pieces_db
            new_pieces_kw_function_name = "kw_match_" + new_pieces_db
    
    parent_game_options = ["No"] + games
    parent_game_menu = TerminalMenu(
        parent_game_options,
        title="Does this game have a parent game?"
    )
    parent_game_index = parent_game_menu.show()
    if parent_game_index != 0:
        new_parent_game = parent_game_options[parent_game_index]
    
    # based on https://www.geeksforgeeks.org/executing-sql-query-with-psycopg2-in-python/
    # TODO this is to to be able to run SQL to create the tables and the functions for the game
    conn = psycopg2.connect( 
        database="geeks", user='postgres', 
        password='root', host='localhost', port='5432'
    ) 
    
    conn.autocommit = True
    cursor = conn.cursor() 
    
    sql = "insert into employee values('191351','divit','100000.0'),('191352','rhea','70000.0');"
    
    cursor.execute(sql) 
    
    conn.commit() 
    conn.close()
    
    # TODO this is to insert the row into the games table with all the fields
    supa_client.table('countries').insert({"id": 1, "name": "Denmark"}).execute()
    
    # TODO create the game file in this directory
        