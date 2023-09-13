import requests
from langchain.vectorstores import SupabaseVectorStore
from langchain.embeddings.openai import OpenAIEmbeddings
import configparser

config = configparser.ConfigParser()
config.read('keys.cfg')

embeddings = OpenAIEmbeddings(openai_api_key=config.get('OpenAI', 'key'))

def web_downloader(website, file_name, file_format):
    query_parameters = {"downloadformat": f"{file_format}"}
    response = requests.get(website, params=query_parameters)
    print(f"{file_name} done fetching")
    return response.json()

def supa_trainer(table, documents, supa_client):
    #TODO add the database wipe here
    SupabaseVectorStore.from_documents(documents, embeddings, client=supa_client,
                                       table_name=table, show_progress=True)
    
def supa_compare(supa_client):
    return

