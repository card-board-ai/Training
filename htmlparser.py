from bs4 import BeautifulSoup
import requests

page = requests.get("https://magic.wizards.com/en/rules")

soup = BeautifulSoup(page.content, "html.parser")

print(page.text)
