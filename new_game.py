from simple_term_menu import TerminalMenu
import psycopg2


def create_game(games_table, supa_client, environemnt, config):
    games = []
    for item in games_table.data:
        name = item.get('game')
        games.append(name.casefold().replace(" ", "_"))
    
    # define the names of all required fields
    new_game_name: str = ""
    while new_game_name == "" or new_game_name.casefold().replace(" ", "_") in games:
        new_game_name = input("New Game Name: ")
        if new_game_name.casefold().replace(" ", "_") in games:
            print("That game alreday exists")

    new_file_name = new_game_name.casefold().replace(" ","_")
    new_rules_db = new_game_name.casefold().replace(" ", "_") + "_rules"
    new_rules_sq_function_name = "match_" + new_rules_db
    new_rules_kw_function_name = "kw_match_" + new_rules_db
    
    pieces_options = ["No", "Yes"]
    pieces_menu = TerminalMenu(
        pieces_options,
        title="Does this game need a pieces db?"
    )
    pieces_index = pieces_menu.show()
    match pieces_options[pieces_index]:
        case "Yes":
            new_pieces_db = new_game_name.casefold().replace(" ", "_") + "_pieces"
            new_pieces_sq_function_name = "match_" + new_pieces_db
            new_pieces_kw_function_name = "kw_match_" + new_pieces_db
        case _:
            new_pieces_db = None
            new_pieces_sq_function_name = None
            new_pieces_kw_function_name = None

    parent_game_options = ["No"] + games
    parent_game_menu = TerminalMenu(
        parent_game_options,
        title="Does this game have a parent game?"
    )
    parent_game_index = parent_game_menu.show()
    if parent_game_options[parent_game_index] != "No":
        new_parent_game = parent_game_options[parent_game_index]
    else:
        new_parent_game = None

    # this is to insert the row into the games table with all the fields, the option values here
    # are nullable in the db so passing none in the insert should be fine
    supa_client.table('games').insert({"game": new_game_name, "rules_db": new_rules_db,
                                       "pieces_db": new_pieces_db, "parent_game": new_parent_game,
                                       "training_file": new_file_name,
                                       "piecesSimilarityQueryName": new_pieces_sq_function_name,
                                       "piecesKeywordQueryName": new_pieces_kw_function_name,
                                       "rulesSimilarityQueryName": new_rules_sq_function_name,
                                       "rulesKeywordQueryName": new_rules_kw_function_name}).execute()

    # this is to to be able to run SQL to create the tables and the functions for the game
    call_postgres(new_rules_db, new_rules_sq_function_name, new_rules_kw_function_name, config, environemnt)
    if pieces_options[pieces_index] == "Yes" and new_pieces_db is not None:
        call_postgres(new_pieces_db, new_pieces_sq_function_name, new_pieces_kw_function_name, config, environemnt)

    # TODO look into doing this in git so that it can create its own branch and create the file there
    # this creates the game file in this directory
    open(f"{new_file_name}.py", "wb").close()


def call_postgres(table_name: str, sim_q_name: str, key_q_name: str, config, environemnt):
    # based on https://www.geeksforgeeks.org/executing-sql-query-with-psycopg2-in-python/
    conn = psycopg2.connect(
        database=config.get(f'Postgress {environemnt}', 'database'),
        user=config.get(f'Postgress {environemnt}', 'user'),
        password=config.get(f'Postgress {environemnt}', 'password'),
        host=config.get(f'Postgress {environemnt}', 'host'),
        port=config.get(f'Postgress {environemnt}', 'port'))

    conn.autocommit = True
    cursor = conn.cursor() 

    # the double curles in similarity serach create function are double instead of
    # single becasuse of python fstring interpolation
    sql = f'''-- Create a table to store your documents
                create table {table_name} (
                  id uuid primary key,
                  content text, -- corresponds to Document.pageContent
                  metadata jsonb, -- corresponds to Document.metadata
                  embedding vector(1536) -- 1536 works for OpenAI embeddings, change if needed
                );

                -- Create a function to similarity search for documents
                create function {sim_q_name} (
                  query_embedding vector(1536),
                  match_count int,
                  filter jsonb DEFAULT '{{}}'
                ) returns table (
                  id uuid,
                  content text,
                  metadata jsonb,
                  similarity float
                )
                language plpgsql
                as $$
                #variable_conflict use_column
                begin
                  return query
                  select
                    id,
                    content,
                    metadata,
                    1 - ({table_name}.embedding <=> query_embedding) as similarity
                  from {table_name}
                  where metadata @> filter
                  order by {table_name}.embedding <=> query_embedding
                  limit match_count;
                end;
                $$;

                -- Create a function to keyword search for documents
                create function {key_q_name}(query_text text, match_count int)
                returns table (id uuid, content text, metadata jsonb, similarity real)
                as $$

                begin
                return query execute
                format('select id, content, metadata, ts_rank(to_tsvector(content), plainto_tsquery($1)) as similarity
                from {table_name}
                where to_tsvector(content) @@ plainto_tsquery($1)
                order by similarity desc
                limit $2')
                using query_text, match_count;
                end;
                $$ language plpgsql;
'''

    cursor.execute(sql)
    conn.commit() 
    conn.close()
    