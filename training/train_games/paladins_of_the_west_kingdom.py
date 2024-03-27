from langchain.document_loaders import PyMuPDFLoader
from .train_game import TrainGame
from ..external_comm import web_downloader, supa_trainer
import os


class paladins_of_the_west_kingdom(TrainGame):
    def paladins_of_the_west_kingdom_rules(self):
        print(str(self.games.data))
        rules_file = web_downloader(self.config.get('Sources', 'paladins_of_the_west_kingdom_rules'),
                                    "Paladins of the West Kingdom", "pdf")
        rules_location = "./rules.pdf"
        pdf = open(rules_location, 'wb')
        pdf.write(rules_file)
        loader = PyMuPDFLoader(rules_location)
        docs = loader.load_and_split()
        supa_trainer("paladins_of_the_west_kingdom_rules", "Paladins of the West Kingdom",
                     self.supa_client, self.supa_key, rules_file, "pdf", docs, rules_location)
        os.remove(rules_location)
        print("Paladins of the West Kingdom rules trained")
