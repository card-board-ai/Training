from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import SupabaseVectorStore
from datetime import datetime, timezone
from rich.console import Console
from hashlib import blake2b
from rich import print
import configparser
import requests
import json

console = Console()

config = configparser.ConfigParser()
config.read('keys.cfg')

embeddings = OpenAIEmbeddings(openai_api_key=config.get('OpenAI', 'key'))


def web_downloader(website, file_name, file_format):
    # special case for lorcana cards because the api is not responding well to the way I normally grab json
    # this has to be json encoded in the lorcana file so that each card can be trained individually
    if file_format == "json" and file_name == "lorcana cards":
        response = requests.get(website)
        return response.content
    elif file_format == "json" or file_format == "txt":
        query_parameters = {"downloadformat": f"{file_format}"}
        response = requests.get(website, params=query_parameters)
    elif file_format == "pdf":
        # https://techbit.ca/2022/12/downloading-pdf-files-using-python/
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; rv:108.0) Gecko/20100101 Firefox/108.0'
        }
        response = requests.get(website, headers=headers, stream=True)
    else:
        raise Exception("web_downloader can not handle that file type")
    print(f"{file_name} done fetching")
    # same special case as line 17 mentions
    if file_format == "json" and file_name != "lorcana cards":
        return response.json()
    elif file_format == "txt" or file_format == "pdf":
        return response.content


def supa_trainer(table, game, supa_client, supa_auth, file, file_format, documents, file_location):
    data, count = supa_client.table("training_ledger") \
        .select('hash') \
        .eq('db_table', table) \
        .order('created_at', desc=True) \
        .execute()
    new_file_hash = gen_hash(file, file_format)

    if hash_compare(data, new_file_hash):
        print(f"{table} is being trained")
        headers = {"Content-Type": "application/json", "Authorization": str(supa_auth)}
        data = {"table": table}
        dbwipe_response = requests.post(config.get('Supabase', 'table_wipe_url'), 
                                        headers=headers, json=data)
        print("vectorDbWipe server respons =" + str(dbwipe_response))
        filename = f"{table}-{datetime.now(timezone.utc)}.{file_format}"
        print("filename = " + filename)
        bucket_list = supa_client.storage.list_buckets()
        print(bucket_list)
        for bucket in bucket_list:
            if bucket.name == table:
                break
        else:
            supa_client.storage.create_bucket(table)
        up_response = supa_client.storage.from_(str(table)).upload(file=file_location, path=filename)
        print("uploading to supabase url" + str(up_response))    
        supa_list = supa_client.storage.from_(str(table)).list()
        print(supa_list)
        file_id = next((item['id'] for item in supa_list if item['name'] == filename), None)
        SupabaseVectorStore.from_documents(documents, embeddings, client=supa_client,
                                           table_name=table, show_progress=True)
        supa_client.table('training_ledger') \
            .insert({"file_id": file_id, "file_name": filename, "hash": new_file_hash,
                     "db_table": table, "game": game}) \
            .execute()
    else:
        console.print(f"{table} does not need to be trained", style="bold red")


def gen_hash(file, file_format: str):
    if file_format == "json":
        encoded = json.dumps(file_format, sort_keys=True).encode()
        return blake2b(encoded).hexdigest()
    else:
        return blake2b(file).hexdigest()


def hash_compare(previous, current):
    if previous[1]:
        # Check the provided hash against the first hash in the response data
        if previous[1][0].get('hash') == current:
            return False
        else:
            return True
    else:
        # Handle the case where there are no hash values in the response
        return True
