from external_comm import downloader

rulings_dict = {}
exclude_properties = ['id', 'lang', 'multiverse_ids', 'mtgo_id', 'mtgo_foil_id',
                          'tcgplayer_id', 'cardmarket_id', 'uri', 'scryfall_uri',
                          'layout', 'highres_image', 'image_status', 'image_uris',
                          'set_id', 'set_uri', 'set_search_uri', 'scryfall_set_uri',
                          'rulings_uri', 'prints_search_uri', 'card_back_id',
                          'flavor_text', 'artist_ids', 'illustration_id',
                          'border_color', 'frame', 'full_art', 'textless',
                          'booster', 'story_spotlight', 'edhrec_rank', 'prices',
                          'related_uris', 'tcgplayer_infinite_articles',
                          'tcgplayer_infinite_decks', 'edhrec', 'security_stamp',
                          'preview', 'penny_rank', 'variation', 'arena_id', 'oversized',
                          'promo', 'reprint', 'variation', 'all_parts', 'artist_id',
                          'games', 'foil', 'nonfoil', 'finshes', 'set',
                          'collector_number', 'purchase_uris']
exclude_set_types = ['memorabilia', 'minigame', 'funny', 'token']

def json_merger():
    # Iterate over FileA(rullings) and create a dictionary of rulings based on oracle_id
    for item in file_a:
        oracle_id = item['oracle_id']
        comment = item['comment']
        if oracle_id not in rulings_dict:
            rulings_dict[oracle_id] = []
        rulings_dict[oracle_id].append(comment)

    for item in file_b[:]: #iterating over each card in file b
        #This iterates over each item in 'exclude_set_types', removing on match
        for prop in exclude_set_types:
            if item['set_type'] == prop:
                file_b.remove(item)
                break

    for item in file_b:
        oracle_id = item['oracle_id']
        if item['oracle_id'] in rulings_dict: #This add the rulings to each card
            item['rulings'] = rulings_dict[oracle_id]
        #This removes the properties in 'exclude_properties' from each card
        for prop in exclude_properties:
            item.pop(prop, None)
            if 'card_faces' in item: #removes the prop in the nested card faces
                for face in item['card_faces']:
                    face.pop(prop, None)
    # old code for write the merged data to a new file
    # with open('../finished_file_new.json', 'w') as file:
    #     json.dump(file_b, file, indent=1, ensure_ascii=False)
    #     print('new finsish_file created')
    return file_b

def magic_cards_loader():
    # https://scryfall.com/docs/api/bulk-data/all
    fetched_data = downloader("https://api.scryfall.com/bulk-data",
                          "scryfall_bulk_data", "json")
    for item in fetched_data['data']:
        if item['type'] == "oracle_cards":
            global file_b
            file_b = downloader(item['download_uri'], item['type'], "json")
        elif item['type'] == "rulings":
            global file_a
            file_a = downloader(item['download_uri'], item['type'], "json")
    json_merger()
    return file_b
