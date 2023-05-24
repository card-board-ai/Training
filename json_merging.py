import json
from tqdm import tqdm
from langchain.document_loaders import JSONLoader
from pprint import pprint
from pathlib import Path

with open('../rulings-20230507090027.json', 'r') as file:
    file_a = json.load(file)

with open('../oracle-cards-20230507210415.json', 'r') as file:
    file_b = json.load(file)

rulings_dict = {}
exclude_properties = ['id', 'lang', 'multiverse_ids', 'mtgo_id', 'mtgo_foil_id', 'tcgplayer_id', 'cardmarket_id', 'uri', 'scryfall_uri', 'layout',
                          'highres_image', 'image_status', 'image_uris', 'set_id', 'set_uri', 'set_search_uri', 'scryfall_set_uri', 'rulings_uri',
                           'prints_search_uri', 'card_back_id', 'flavor_text', 'artist_ids', 'illustration_id', 'border_color', 'frame', 'full_art', 'textless',
                            'booster', 'story_spotlight', 'edhrec_rank', 'prices', 'related_uris', 'tcgplayer_infinite_articles', 'tcgplayer_infinite_decks',
                             'edhrec', 'security_stamp', 'preview', 'penny_rank' ]

# Iterate over File B and modify the data
with tqdm(total=len(file_b), desc="Merging data", unit="object") as pbar:
    for item in file_a:
        oracle_id = item['oracle_id']
        comment = item['comment']
        if oracle_id not in rulings_dict:
            rulings_dict[oracle_id] = []
        rulings_dict[oracle_id].append(comment)

    # Iterate over the data from File B, add rulings (if any), and remove unwanted properties
    for item in file_b:
        oracle_id = item['oracle_id']
        if oracle_id in rulings_dict:
            item['rulings'] = rulings_dict[oracle_id]
        for prop in exclude_properties:
            item.pop(prop, None)
        pbar.update(1)

# Write the modified data to a new file
with open('../finsihed_file.json', 'w') as file:
    json.dump(file_b, file, indent=4)
    print("New file created")
