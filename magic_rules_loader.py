from bs4 import BeautifulSoup
from simple_term_menu import TerminalMenu
import requests
from external_comm import downloader

rules_page = requests.get("https://magic.wizards.com/en/rules")

soup = BeautifulSoup(rules_page.content, "html.parser")

file_links = []
links = soup.find_all("a")
for link in links:
    link_url = link["href"]
    if ".txt" in link_url:
        file_links.append(link_url)

if len(file_links) > 1:
    terminal_menu = TerminalMenu(file_links)
    choice_index = terminal_menu.show()
    downloader(file_links[choice_index], "rules", "txt")
elif file_links.count == 0:
    raise Exception ("0 text files paresed from magic rules website")
else:
    downloader(file_links[0], "rules", "txt")
