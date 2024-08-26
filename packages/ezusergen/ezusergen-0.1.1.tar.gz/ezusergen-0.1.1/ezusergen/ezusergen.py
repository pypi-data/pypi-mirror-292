#imports (barebones 1.2)
import requests
import random

# logic
def generate(length=None):
    if length is None or not isinstance(length, int):
        length = 7
    url = f'https://random-word-api.herokuapp.com/word?length={length}'
    resp = requests.get(url=url)
    resp2 = requests.get(url=url)
    data = [word.capitalize() for word in (resp.json() + resp2.json())]
    randomnum = random.randint(127, 999)
    final = ''.join(data) + str(randomnum)

    return final
