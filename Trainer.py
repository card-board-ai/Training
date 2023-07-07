import os
import configparser
import json
from tqdm import tqdm
from pprint import pprint
from pathlib import Path
from supabase.client import Client, create_client
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import SupabaseVectorStore
from langchain.document_loaders import TextLoader
from langchain.document_loaders import JSONLoader

config = configparser.ConfigParser()
config.read('keys.cfg')

embeddings = OpenAIEmbeddings(openai_api_key=config.get('OpenAI', 'key'))

environment = input("Which environment are we training, local or prod?: ")
if environment == "local":
    supabase: Client = create_client(config.get('Supabase', 'local_url'), config.get('Supabase', 'local_key'))
elif environment == "prod":
    supabase: Client = create_client(config.get('Supabase', 'prod_url'), config.get('Supabase', 'prod_private_key'))
else:
    raise Exception("That is not an available environment")

#TODO have this text splitter split each rule individually instead of in deefined chunks. I believe you can have it
#split into chunks based on numbers or line breaks and other stuff
rules = input("Do you want to train Rules? y/n: ")
if rules == "y":
    loader = TextLoader("../MagicRulesApril14.txt")
    documents = loader.load()
    text_splitter = CharacterTextSplitter(chunk_size=600, chunk_overlap=100)
    rules_docs = text_splitter.split_documents(documents)
    SupabaseVectorStore.from_documents(
    rules_docs, embeddings, client=supabase, table_name="rules", show_progress=True)
elif rules == "n":
    print("Not training rules data")
    rules_docs = []
else:
    raise Exception("That is not y or n")


cards = input("Do you want to train cards? y/n: ")
if cards == "y":
    with open('../rulings-20230507090027.json', 'r') as file:
        file_a = json.load(file)
    with open('../oracle-cards-20230507210415.json', 'r') as file:
        file_b = json.load(file)
    rulings_dict = {}
    exclude_properties = ['id', 'lang', 'multiverse_ids', 'mtgo_id', 'mtgo_foil_id', 'tcgplayer_id', 'cardmarket_id', 'uri', 'scryfall_uri', 'layout',
                          'highres_image', 'image_status', 'image_uris', 'set_id', 'set_uri', 'set_search_uri', 'scryfall_set_uri', 'rulings_uri',
                           'prints_search_uri', 'card_back_id', 'flavor_text', 'artist_ids', 'illustration_id', 'border_color', 'frame', 'full_art', 'textless',
                            'booster', 'story_spotlight', 'edhrec_rank', 'prices', 'related_uris', 'tcgplayer_infinite_articles', 'tcgplayer_infinite_decks',
                             'edhrec', 'security_stamp', 'preview', 'penny_rank', 'variation', 'arena_id', 'oversized', 'promo', 'reprint', 'variation',
                              "all_parts" ]
    def json_merger():
        with tqdm(total=len(file_b), desc="Merging data", unit="object") as pbar:
    # Iterate over File B and modify the data
            for item in file_a:
                oracle_id = item['oracle_id']
                comment = item['comment']
                if oracle_id not in rulings_dict:
                    rulings_dict[oracle_id] = []
                    rulings_dict[oracle_id].append(comment)
    # Iterate over the data from File B, add rulings (if any), and remove unwanted properties
    #TODO this is removing the first level properties but double faced cards have properties in deeper levels that also have properties we should removerin
            for item in file_b:
                oracle_id = item['oracle_id']
                if oracle_id in rulings_dict:
                    item['rulings'] = rulings_dict[oracle_id]
                for prop in exclude_properties:
                    item.pop(prop, None)
                pbar.update(1)    
    # Write the merged data to a new file
            with open('../finsihed_file.json', 'w') as file:
                json.dump(file_b, file, indent=4)
                print(f'new file created')
    if Path('../finsihed_file.json').is_file:
        new_file = input("Do you want to create a new merged JSON file? y/n: ")
        if new_file == "y":
            json_merger()
        elif new_file =="n":
            print("not making a new merged json file")
        else:
            raise Exception("That is not y or n")
    else:
        json_merger()
    loader = JSONLoader(
    file_path='../finsihed_file.json',
    jq_schema='.[] | tostring')
    card_docs = loader.load()
    SupabaseVectorStore.from_documents(
    card_docs, embeddings, client=supabase, table_name="cards", show_progress=True)
elif cards == "n":
    print("Not training cards")
    card_docs = []
else:
    raise Exception("That is not y or n")

print("Done")