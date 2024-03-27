from langchain.document_loaders import PyPDFLoader
from langchain.document_loaders import JSONLoader
from ..external_comm import web_downloader, supa_trainer
import json
import os


def lorcana_rules(supa_client, supa_key, config):
    rules_file = web_downloader(config.get('Sources', 'lorcana_rules'),
                                              "lorcana rules", "pdf")
    rules_location = "./rules.pdf"
    pdf = open(rules_location, 'wb')
    pdf.write(rules_file)
    loader = PyPDFLoader(rules_location)
    docs = loader.load_and_split()
    supa_trainer("lorcana_rules", "Lorcana", supa_client, supa_key,
                               rules_file, "pdf", docs, rules_location)
    os.remove(rules_location)
    print("rules loaded")


# TODO perge the cards json for things the ai doens't need
def lorcana_cards(supa_client, supa_key, config):
    # this web downloader specifies json when actually it is
    # going to retrieve txt because the api for lorcana cards is bad
    cards = web_downloader(config.get('Sources', 'lorcana_cards'),
                                         "lorcana cards", "json")
    json_cards = json.loads(cards)
    cards_location = "./lorcana_cards.json"
    with open(cards_location, 'w') as file:
        json.dump(json_cards, file, indent=1, ensure_ascii=False)
        print(f'{cards_location} saved')
    loader = JSONLoader(
        file_path=cards_location,
        jq_schema='.[] | tostring')
    card_docs = loader.load()
    print("loader loaded")
    supa_trainer("lorcana_cards", "Lorcana", supa_client, supa_key,
                               cards, "json", card_docs, cards_location)
    os.remove(cards_location)
    print("cards loaded")
