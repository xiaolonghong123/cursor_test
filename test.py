import requests
from rich import print
r = requests.get("https://api.github.com")
print(r.json())