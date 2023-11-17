from langchain.document_loaders import PyMuPDFLoader
import external_comm
import os


def eclipse_new_dawn_for_the_galaxy_rules(supa_client, supa_key, config):
    rules_file = external_comm.web_downloader(config.get('Sources', 'eclipse_new_dawn_for_the_galaxy_rules'),
                                              "Eclipse New Dawn for the Galaxy rules", "pdf")
    rules_location = "./rules.pdf"
    pdf = open(rules_location, 'wb')
    pdf.write(rules_file)
    loader = PyMuPDFLoader(rules_location)
    docs = loader.load_and_split()
    external_comm.supa_trainer("eclipse_new_dawn_for_the_galaxy_rules", "Eclipse New Dawn for the Galaxy",
                               supa_client, supa_key, rules_file, "pdf", docs, rules_location)
    os.remove(rules_location)
    print("Eclipse New Dawn for the Galaxy rules loaded")