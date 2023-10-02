from datetime import datetime, timezone
import requests
from langchain.embeddings.openai import OpenAIEmbeddings
import configparser
from hashlib import blake2b

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
    print("vectorDbWipe server respons =" + str(dbwipe_response))
    filename = f"/{table}-{datetime.now(timezone.utc)}.{file_format}"
    up_response = supa_client.storage.from_(str(table)).upload(filename, file)
    print("uploading to supabase url" + str(up_response))
    print(supa_client.storage.from_(str(table)).list())
    # SupabaseVectorStore.from_documents(documents, embeddings, client=supa_client,
    #                                    table_name=table, show_progress=True)

def hash (file):
    sum = blake2b(file).hexdigest()
    return sum

def compare (previous, current):
    if previous == current:
        return True
    else:
        return False

