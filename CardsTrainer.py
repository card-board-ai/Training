import os
import configparser
from supabase.client import Client, create_client
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import SupabaseVectorStore
from langchain.document_loaders import JSONLoader
import json
from pathlib import Path
from pprint import pprint

config = configparser.ConfigParser()
config.read('keys.cfg')

environment = input("Which environment are we training, local or prod?")

if environment == "local":
    supabase: Client = create_client(config.get('Supabase', 'local_url'), config.get('Supabase', 'local_key'))
elif environment == "prod":
    supabase: Client = create_client(config.get('Supabase', 'prod_url'), config.get('Supabase', 'prod_private_key'))
else:
    raise Exception("That is not an available environment")

loader = JSONLoader(
    file_path='../default-cards-20230506211056.json',
    jq_schema='.messages[].content')

data = loader.load()
