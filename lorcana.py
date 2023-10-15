from langchain.document_loaders import PyPDFLoader
from langchain.document_loaders import JSONLoader
import external_comm
import json
import os


def lorcana_rules(supa_client, supa_key, config):
    rules_file = external_comm.web_downloader(config.get('Sources', 'lorcana_rules'),
                                              "lorcana rules", "pdf")
    rules_location = "./rules.pdf"
    pdf = open(rules_location, 'wb')
    pdf.write(rules_file)
    loader = PyPDFLoader(rules_location)
    docs = loader.load_and_split()
    external_comm.supa_trainer("lorcana_rules", "Lorcana", supa_client, supa_key,
                               rules_file, "pdf", docs, rules_location)
    os.remove(rules_location)
    print("rules loaded")


def lorcana_cards(supa_client, supa_key, config):
    cards = external_comm.web_downloader(config.get('Sources', 'lorcana_cards'),
                                         "lorcana cards", "txt")
    cards_location = "./lorcana_cards.json"
    print(cards)
    with open(cards_location, 'w') as file:
        json.dump(cards, file, indent=1, ensure_ascii=False)
        print(f'{cards_location} saved')
    loader = JSONLoader(
        file_path=cards_location,
        jq_schema='.[] | tostring')
    card_docs = loader.load()
    print("loader loaded")
    external_comm.supa_trainer("lorcana_cards", "Lorcana", supa_client, supa_key,
                               cards, "json", card_docs)
    os.remove(cards_location)
    print("cards loaded")
