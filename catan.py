from langchain.document_loaders import PyPDFLoader
import external_comm
import os


def catan_rules(supa_client, supa_key):
    rules_file = external_comm.web_downloader("https://www.catan.com/sites/default/files/2021-06/catan"
                                              "_base_rules_2020_200707.pdf", "catan rules", "pdf")
    rules_location = "./rules.pdf"
    pdf = open(rules_location, 'wb')
    pdf.write(rules_file)
    loader = PyPDFLoader(rules_location)
    docs = loader.load_and_split()
    os.remove(rules_location)
    external_comm.supa_trainer("catan_rules", "Settlers of Catan", supa_client, supa_key,
                               rules_file, "pdf", docs)
    print("Catan rules loaded")
    