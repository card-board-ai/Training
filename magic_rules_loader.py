from bs4 import BeautifulSoup
from simple_term_menu import TerminalMenu
import requests

def downloader(website):
    query_parameters = {"downloadformat": "txt"}
    response = requests.get(website, params=query_parameters)  
    with open("rules.txt", mode="wb") as file:
        file.write(response.content)
    print("done")

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
    downloader(choice_index)
elif file_links.count == 0:
    raise Exception ("0 text files paresed from magic rules website")
else:
    downloader(file_links[0])
