#imports (barebones 1.2)
import requests
import random

# logic (updated)
def generate(length=None, noNum=None):
    if length is None or not isinstance(length, int):
        length = 7
    url = f'https://random-word-api.herokuapp.com/word?length={length}'
    resp = requests.get(url=url)
    resp2 = requests.get(url=url)
    data = [word.capitalize() for word in (resp.json() + resp2.json())]
    randomnum = random.randint(127, 999)
    if noNum is None or noNum is False:
        final = ''.join(data) + str(randomnum)
    elif noNum is True:
        final = ''.join(data)
    
    return final
