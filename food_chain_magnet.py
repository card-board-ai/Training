from langchain.document_loaders import PyMuPDFLoader
import external_comm
import os


def food_chain_magnet_rules(supa_client, supa_key, config):
    rules_file = external_comm.web_downloader(config.get('Sources', 'food_chain_magnet_rules'),
                                              "Food Chain Magnet rules", "pdf")
    rules_location = "./rules.pdf"
    pdf = open(rules_location, 'wb')
    pdf.write(rules_file)
    loader = PyMuPDFLoader(rules_location)
    docs = loader.load_and_split()
    external_comm.supa_trainer("food_chain_magnet_rules", "Food Chain Magnet",
                               supa_client, supa_key, rules_file, "pdf", docs, rules_location)
    os.remove(rules_location)
    print("food chain magnet rules loaded")
    