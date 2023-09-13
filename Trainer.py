import configparser
import json
import os
from supabase.client import Client, create_client
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import SupabaseVectorStore
from langchain.document_loaders import TextLoader
from langchain.document_loaders import JSONLoader
from magic_cards_loader import magic_cards_loader

config = configparser.ConfigParser()
config.read('keys.cfg')

embeddings = OpenAIEmbeddings(openai_api_key=config.get('OpenAI', 'key'))

environment = input("Which environment are we training, local or prod?: ")
if environment == "local":
    supabase: Client = create_client(config.get('Supabase', 'local_url'), 
                                     config.get('Supabase', 'local_key'))
elif environment == "prod":
    supabase: Client = create_client(config.get('Supabase', 'prod_url'), 
                                     config.get('Supabase', 'prod_private_key'))
elif environment == "none":
    pass
else:
    raise Exception("That is not an available environment")

#TODO have this text splitter split each rule individually instead of in deefined chunks
#I believe you can have is split into chunks based on when it finds a formated numbers
# or line breaks and other stuff
rules = input("Do you want to train Rules? y/n: ")
if rules == "y":
    rules_file = magic_cards_loader()
    rules_location = "./rules.txt"
    with open(rules_location, 'w') as file:
        json.dump(rules_file, file, indent=1, ensure_ascii=False)
        print(f'{rules_location} saved')
    loader = TextLoader(rules_location)
    documents = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, 
                                                   chunk_overlap=200, 
                                                   length_function = len)
    rules_docs = text_splitter.split_documents(documents)
    os.remove(rules_location)
    SupabaseVectorStore.from_documents(
    rules_docs, embeddings, client=supabase, table_name="rules", show_progress=True)
elif rules == "n":
    print("Not training rules data")
    rules_docs = []
else:
    raise Exception("That is not y or n")

cards = input("Do you want to train cards? y/n: ")
if cards == "y":
    finished_file = magic_cards_loader()
    cards_location = "./merged_file.json"
    with open(cards_location, 'w') as file:
        json.dump(finished_file, file, indent=1, ensure_ascii=False)
        print(f'{cards_location} saved')
    loader = JSONLoader(
        file_path=cards_location,
        jq_schema='.[] | tostring')
    card_docs = loader.load()
    print("loader loaded")
    os.remove(cards_location)
    SupabaseVectorStore.from_documents(
        card_docs, embeddings, client=supabase, table_name="cards", 
        show_progress=True)
elif cards == "n":
    print("Not training cards")
    card_docs = []
else:
    raise Exception("That is not y or n")

print("Done")