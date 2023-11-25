from langchain.document_loaders import PyMuPDFLoader
import external_comm
import os


def aeon_trespass_odyssey_rules(supa_client, supa_key, config):
    rules_file = external_comm.web_downloader(config.get('Sources', 'aeon_trespass_odyssey_rules'),
                                              "Aeon Trspass Odyssey rules", "googlepdf")
    rules_location = "./rules.pdf"
    pdf = open(rules_location, 'wb')
    pdf.write(rules_file)
    loader = PyMuPDFLoader(rules_location)
    docs = loader.load_and_split()
    external_comm.supa_trainer("aeon_trespass_odyssey_rules", "Aeon Trespass Odyssey",
                               supa_client, supa_key, rules_file, "pdf", docs, rules_location)
    os.remove(rules_location)
    print("Aeon Trespass Odyssey rules loaded")
    