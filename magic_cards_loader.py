import requests

# https://scryfall.com/docs/api/bulk-data/all
url_fetch = requests.get("https://api.scryfall.com/bulk-data")

def downloader(website, file):
    query_parameters = {"downloadformat": "json"}
    response = requests.get(website, params=query_parameters)  
    with open(f"{file}.json", mode="wb") as file:
        file.write(response.content)
    print(f"{file} done downloading")

fetched_data = url_fetch.json()
for item in fetched_data['data']:
    if item['type'] == "oracle_cards" or item['type'] == "rulings":
        downloader(item['download_uri'], item['type'])

