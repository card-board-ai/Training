from rich import print
from datetime import datetime, timezone
import requests
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import SupabaseVectorStore
from datetime import datetime, timezone
from hashlib import blake2b
from rich import print
import configparser
import requests

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


def supa_trainer(table, game, supa_client, supa_auth, file, file_format, documents):
    data, count = supa_client.table("training_ledger") \
        .select('hash') \
        .eq('db_table', table) \
        .order('created_at', desc=True) \
        .execute()
    new_file_hash = gen_hash(file)

    if compare(data, new_file_hash):
        print(f"{table} is being trained")
        headers = {"Content-Type": "application/json", "Authorization": str(supa_auth)}
        data = {"table": table}
        dbwipe_response = requests.post(config.get('Supabase', 'table_wipe_url'), 
                                        headers=headers, json=data)
        print("vectorDbWipe server respons =" + str(dbwipe_response))
        filename = f"{table}-{datetime.now(timezone.utc)}.{file_format}"
        print("filename = " + filename)
        up_response = supa_client.storage.from_(str(table)).upload(filename, file)
        print("uploading to supabase url" + str(up_response))    
        supa_list = supa_client.storage.from_(str(table)).list()
        print(supa_list)
        file_id = next((item['id'] for item in supa_list if item['name'] == filename), None)
        supa_client.table('training_ledger') \
            .insert({"file_id": file_id, "file_name": filename, "hash": new_file_hash,
                    "db_table": table, "game": game}) \
            .execute()
        SupabaseVectorStore.from_documents(documents, embeddings, client=supa_client,
                                           table_name=table, show_progress=True)
    else:
        print(f"{table} does not need to be trained")


def gen_hash(file):
    return blake2b(file).hexdigest()


def compare(previous, current):
    if previous[1]:
        # Check the provided hash against the first hash in the response data
        if previous[1][0].get('hash') == current:
            return False
        else:
            return True
    else:
        # Handle the case where there are no hash values in the response
        return True
