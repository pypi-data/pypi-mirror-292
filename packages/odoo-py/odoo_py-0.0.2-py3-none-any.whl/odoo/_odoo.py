import requests

class Odoo:
    def __init__(self):
        ...

    def get_poke(self):
        response = requests.get("https://pokeapi.co/api/v2/pokemon/ditto")
        return response.json()