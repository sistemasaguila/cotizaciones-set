import json
from decimal import Decimal

import requests
from bs4 import BeautifulSoup

requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS = "ALL:@SECLEVEL=1"


def get_soup(url):
    try:
        soup = BeautifulSoup(
            requests.get(
                url,
                timeout=10,
                headers={"user-agent": "Mozilla/5.0"},
                verify=True,
            ).text,
            "html.parser",
        )
        return soup
    except requests.ConnectionError as e:
        print(f"Connection Error {e}")
    except Exception as e:
        print(e)
    return None


def normalize(number):
    decimal_str = None
    thousands_separator = None
    first_character = None
    second_character = None
    for i, c in enumerate(number):
        try:
            int(c)
        except ValueError:
            if first_character is None:
                first_character = i
            else:
                if c != number[first_character]:
                    second_character = i
                    decimal_str = c
                    thousands_separator = number[first_character]
    if second_character is None:
        decimal_str = number[first_character]
    normalized = number
    if thousands_separator is not None:
        normalized = normalized.replace(thousands_separator, 'T')
    normalized = normalized.replace(decimal_str, 'D')
    return normalized.replace('T', '').replace('D', '.')
    
class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Decimal):
            return str(o)
        return super(DecimalEncoder, self).default(o)
                                                   