import os
import configparser
import json
from supabase.client import Client, create_client
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import SupabaseVectorStore
from langchain.document_loaders import TextLoader

config = configparser.ConfigParser()
config.read('keys.cfg')

environment = input("Which environment are we training, local or prod?")
if environment == "local":
    supabase: Client = create_client(config.get('Supabase', 'local_url'), config.get('Supabase', 'local_key'))
elif environment == "prod":
    supabase: Client = create_client(config.get('Supabase', 'prod_url'), config.get('Supabase', 'prod_private_key'))
else:
    raise Exception("That is not an available environment")

rules = input("Do you want to train Rules? Y/n")
if rules == "Y":
    loader = TextLoader("../MagicRulesApril14.txt")
    documents = loader.load()
    text_splitter = CharacterTextSplitter(chunk_size=300, chunk_overlap=50)
    rules_docs = text_splitter.split_documents(documents)
elif rules == "n":
    print("Not training rules")
else:
    raise Exception("That is not Y or n")

cards = input("Do you want to train cards? Y/n")
if cards == "Y":

elif rules == "n":
    print("Not training rules")
else:
    raise Exception("That is not Y or n")

embeddings = OpenAIEmbeddings(openai_api_key=config.get('OpenAI', 'key'))
SupabaseVectorStore.from_documents(
    rules_docs, embeddings, client=supabase
)

print("Done")