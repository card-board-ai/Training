from langchain.document_loaders import PyMuPDFLoader
import external_comm
import os


def paladins_of_the_west_kingdom_rules(supa_client, supa_key, config):
    rules_file = external_comm.web_downloader(config.get('Sources', 'paladins_of_the_west_kingdom_rules'),
                                              "Paladins of the West Kingdom", "pdf")
    rules_location = "./rules.pdf"
    pdf = open(rules_location, 'wb')
    pdf.write(rules_file)
    loader = PyMuPDFLoader(rules_location)
    docs = loader.load_and_split()
    external_comm.supa_trainer("paladins_of_the_west_kingdom_rules", "Paladins of the West Kingdom",
                               supa_client, supa_key, rules_file, "pdf", docs, rules_location)
    os.remove(rules_location)
    print("Paladins of the West Kingdom rules trained")