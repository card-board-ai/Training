from langchain.document_loaders import PyPDFLoader
import external_comm
import os


def lorcana_rules(supa_client, supa_key):
    print("hi from lorcana rules loader")
    rules_file = external_comm.web_downloader("https://cdn.ravensburger.com/lorcana/quickstart-en",
                                              "lorcana rules", "pdf")
    rules_location = "./rules.pdf"
    with open(rules_location, 'w') as f:
        f.write(str(rules_file))
        print(f'{rules_location} saved')
    loader = PyPDFLoader(rules_location)
    docs = loader.load_and_split()
    os.remove(rules_location)
    external_comm.supa_trainer("lorcana_rules", "Lorcana", supa_client, supa_key,
                               rules_file, "pdf", docs)


def lorcana_cards_loader():

    print("hi from lorcana cards loader")
