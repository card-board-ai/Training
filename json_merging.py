import json
from tqdm import tqdm
from langchain.document_loaders import JSONLoader
from pprint import pprint

with open('../rulings-20230507090027.json', 'r') as file:
    file_a = json.load(file)

with open('../oracle-cards-20230507210415.json', 'r') as file:
    file_b = json.load(file)

result = []
matching_items = []

with tqdm(total=len(file_b), desc="Merging data", unit="object") as pbar:
    for item_b in file_b:
        if 'oracle_id' not in item_b:
            result.append(item_b)
            continue
        matching_items = [item_a for item_a in file_a if item_a['oracle_id'] == item_b['oracle_id']]
        rulings = [item_a['comment'] for item_a in matching_items if 'comment' in item_a]
        if rulings:
            item_b_copy = item_b.copy()
            item_b_copy['comment'] = rulings
            result.append(item_b_copy)
        else:
            result.append(item_b)
        pbar.update(1)

# Write the merged data to a new file
with open('../finsihed_file.json', 'w') as file:
    json.dump(result, file)
    print(f'new file created - with {len(file)} objects')

loader = JSONLoader(
    file_path='../finsihed_file.json',
    jq_schema='.[].name')

data = loader.load()

pprint(data)
