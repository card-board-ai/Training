from langchain.document_loaders import PyPDFLoader
import external_comm
import os


def dune_rules(supa_client, supa_key, config):
    rules_file = external_comm.web_downloader(config.get('Sources', 'dune_rules'), "dune rules", "pdf")
    rules_location = "./rules.pdf"
    pdf = open(rules_location, 'wb')
    pdf.write(rules_file)
    loader = PyPDFLoader(rules_location)
    docs = loader.load_and_split()
    external_comm.supa_trainer("dune_rules", "Dune", supa_client, supa_key,
                               rules_file, "pdf", docs, rules_location)
    os.remove(rules_location)
    print("Dune rules loaded")
    