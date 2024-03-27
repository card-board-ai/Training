from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import JSONLoader
from langchain.document_loaders import TextLoader
from simple_term_menu import TerminalMenu
from bs4 import BeautifulSoup
from ..external_comm import web_downloader, supa_trainer
import requests
import json
import os


def magic_cards(supa_client, supa_key, config):
    finished_file = _magic_cards_loader(config)
    cards_location = "./merged_file.json"
    with open(cards_location, 'w') as file:
        json.dump(finished_file, file, indent=1, ensure_ascii=False)
        print(f'{cards_location} saved')
    loader = JSONLoader(
        file_path=cards_location,
        jq_schema='.[] | tostring')
    card_docs = loader.load()
    print("loader loaded")
    supa_trainer("magic_cards", "Magic The Gathering", supa_client, supa_key,
                 finished_file, "json", card_docs, cards_location)
    os.remove(cards_location)


def _json_merger(m_file_a, m_file_b):
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
    rulings_dict = {}
    # Iterate over FileA(rullings) and create a dictionary of rulings based on oracle_id
    for item in m_file_a:
        oracle_id = item['oracle_id']
        comment = item['comment']
        if oracle_id not in rulings_dict:
            rulings_dict[oracle_id] = []
        rulings_dict[oracle_id].append(comment)

    for item in m_file_b[:]:  # iterating over each card in file b
        # This iterates over each item in 'exclude_set_types', removing on match
        for prop in exclude_set_types:
            if item['set_type'] == prop:
                m_file_b.remove(item)
                break

    for item in m_file_b:
        oracle_id = item['oracle_id']
        if item['oracle_id'] in rulings_dict:  # This add the rulings to each card
            item['rulings'] = rulings_dict[oracle_id]
        # This removes the properties in 'exclude_properties' from each card
        for prop in exclude_properties:
            item.pop(prop, None)
            if 'card_faces' in item:  # removes the prop in the nested card faces
                for face in item['card_faces']:
                    face.pop(prop, None)
    return m_file_b


def _magic_cards_loader(config):
    fetched_data = web_downloader(config.get('Sources', 'mtg_cards'),
                                  "scryfall_bulk_data", "json")
    file_b = None
    file_a = None
    for item in fetched_data['data']:
        if item['type'] == "oracle_cards":
            file_b = web_downloader(item['download_uri'],
                                    item['type'], "json")
        elif item['type'] == "rulings":
            file_a = web_downloader(item['download_uri'],
                                    item['type'], "json")

    fin_file_b = _json_merger(file_a, file_b)
    return fin_file_b


# RULES - TODO
""" have this text splitter split each rule individually instead of in deefined chunks
I believe you can have is split into chunks based on when it finds a formated numbers
or line breaks and other stuff """


def magic_rules(supa_client, supa_key, config):
    rules_file = _magic_rules_loader(config)
    rules_location = "./rules.txt"
    with open(rules_location, 'w') as f:
        f.write(str(rules_file))
        print(f'{rules_location} saved')
    loader = TextLoader(rules_location)
    documents = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000,
                                                   chunk_overlap=200,
                                                   length_function=len)
    rules_docs = text_splitter.split_documents(documents)
    supa_trainer("magic_rules", "Magic The Gathering", supa_client, supa_key,
                 rules_file, "txt", rules_docs, rules_location)
    os.remove(rules_location)


def _magic_rules_loader(config):
    rules_page = requests.get(config.get('Sources', 'mtg_rules'))
    file_links = []
    soup = BeautifulSoup(rules_page.content, "html.parser")
    links = soup.find_all("a")
    for link in links:
        link_url = link["href"]
        if ".txt" in link_url:
            file_links.append(link_url)

    if len(file_links) > 1:
        terminal_menu = TerminalMenu(file_links)
        choice_index = terminal_menu.show()
        rules_file = web_downloader(file_links[choice_index],
                                    "rules",
                                    "txt")
        return rules_file
    elif file_links.count == 0:
        raise Exception("0 text files paresed from website")
    else:
        rules_file = web_downloader(file_links[0], "rules", "txt")
        return rules_file
