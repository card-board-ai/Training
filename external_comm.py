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
    if file_format == "json":
        return response.json()
    elif file_format == "txt":
        return response.content
    else:
        raise Exception("web_downloader can not handle that file type")

def supa_trainer(table, documents, supa_client, supa_auth, file, file_format):
    headers = {"Content-Type": "application/json", "Authorization": str(supa_auth)}
    data = {
    "table": table
    }
    dbwipe_response = requests.post(config.get('Supabase', 'table_wipe_url'), 
                             headers=headers, json=data)
    print("vectorDbWipe server respons =" + dbwipe_response)
    up_response = supa_client.storage.from_('training documents').upload(f"/{table}/{table}.{file_format}", file)  # noqa: E501
    print("uploading to supabase respons=" + up_response)
    SupabaseVectorStore.from_documents(documents, embeddings, client=supa_client,
                                       table_name=table, show_progress=True)
    
def supa_compare(supa_client):
    return

