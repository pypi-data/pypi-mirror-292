import requests
import random
from cachetools import cached, TTLCache

cache = TTLCache(maxsize=100, ttl=3600)

@cached(cache)
def conversion_rate(base_currency_code: str, conversion_currency_code: str):
    if type(base_currency_code) !=str or type(conversion_currency_code) != str:
        return "Both base and conversion currency codes must be strings"
    if len(base_currency_code) != 3 or len(conversion_currency_code) != 3:
        return Exception("Currency Code Length should be 3 letters")
        
        
    # tokens = []
    tokens = ["3b7a023bae1963ffa7ec8731","92e81f992503f24b3f1fe64d","961aef8b2d4635904146cd5f",'9b66f315e2586309aacaec73','e6a4e4fb06abe218ed012a6e','c63a3b8400f00d3a6f409b46']


    index = random.randint(0, len(tokens) - 1)  # Fix the index to prevent out-of-bounds error
    url = f"https://v6.exchangerate-api.com/v6/{tokens[index]}/latest/{base_currency_code.upper()}"

    # Fetch the data from the API
    r = requests.get(url)
    data = r.json()
    try:
    # Extract the conversion rate
        conversion_rate = data['conversion_rates'].get(conversion_currency_code.upper())

        if conversion_rate is None:
            raise ValueError(f"Conversion rate not found for {conversion_currency_code}")
        else:
            return conversion_rate
    except Exception as e:
        error = "Error fetching conversion rate, Please try next month or contact with https://github.com/SameerShiekh77"
        return error
    