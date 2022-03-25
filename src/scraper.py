import distutils.dir_util
import json
import os
from collections import ChainMap
from datetime import date
from decimal import Decimal

from utils import DecimalEncoder, get_soup, normalize


MONTHS = {
    "A": "01",
    "B": "02",
    "C": "03",
    "D": "04",
    "E": "05",
    "F": "06",
    "G": "07",
    "H": "08",
    "I": "09",
    "J": "10",
    "K": "11",
    "L": "12",
}
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
SOURCEJSON_URL = os.path.join(BASE_DIR, "source.json")
YEAR_INIT = 2014
CURRENT_YEAR = date.today().strftime("%Y")
CURRENT_MONTH = date.today().strftime("%m")
BASE_URL = "https://www.set.gov.py"
URL = f"{BASE_URL}/portal/PARAGUAY-SET/InformesPeriodicos?folder-id=repository:collaboration:/sites/PARAGUAY-SET/categories/SET/Informes%20Periodicos/cotizaciones-historicos"


def get_months(url):
    months = {}
    soup = get_soup(url)
    if soup:
        for category in soup.select(".SubCategory"):
            path = get_soup(category["href"]).select(".uiContentBox a")[0]["href"]
            title = category["title"]
            month = MONTHS[title.split("-")[0].strip()]
            if int(month) >= get_last_month_processed():
                months[month] = {"link": f"{BASE_URL}{path}"}
    return months


def get_years():
    years = {}
    soup = get_soup(URL)
    if soup:
        for category in soup.select(".SubCategory"):
            year = int(category["title"])
            if year >= YEAR_INIT and year >= get_last_year_processed():
                link = category["href"]
                years[category["title"]] = {"link": link, "months": get_months(link)}
    return years


def get_rates(url, year="2022", month="03"):
    rates = {}
    scheme = {
        "day": {"purchase": None, "sale": None, "cols": (0,)},
        "usd": {"purchase": 1, "sale": 2, "cols": (1, 2)},
        "brl": {"purchase": 3, "sale": 4, "cols": (3, 4)},
        "arp": {"purchase": 5, "sale": 6, "cols": (5, 6)},
        "jpy": {"purchase": 7, "sale": 8, "cols": (7, 8)},
        "eur": {"purchase": 9, "sale": 10, "cols": (9, 10)},
        "gbp": {"purchase": 11, "sale": 12, "cols": (11, 12)},
    }
    soup = get_soup(url)
    date = None
    if soup:
        table = soup.select(".webContentInformation table")[3]
        rows = table.select("tbody > tr")
        for j, row in enumerate(rows):
            if j > 1:
                cols = row.select("td")
                for k, col in enumerate(cols):
                    if k in scheme["day"]["cols"]:
                        date = f"{year}-{month}-{'{:0>2}'.format(col.text)}"
                    else:
                        currency = [x for x in scheme.keys() if k in scheme[x]["cols"]][
                            0
                        ]
                        value = Decimal(normalize(col.text))
                        rate = rates.get(date, None)
                        if rate is None:
                            rates[date] = {
                                currency: {"purchase": Decimal(0), "sale": Decimal(0)}
                            }
                        if rates[date].get(currency, None) is None:
                            rates[date][currency] = {
                                "purchase": Decimal(0),
                                "sale": Decimal(0),
                            }
                        if k == scheme[currency]["purchase"]:
                            rates[date][currency]["purchase"] = value
                        if k == scheme[currency]["sale"]:
                            rates[date][currency]["sale"] = value
    return rates


def update_sourcejson(data):
    with open(SOURCEJSON_URL, "w") as f:
        f.write(json.dumps(data))


def get_sourcejson():
    try:
        with open(SOURCEJSON_URL, "r") as f:
            return json.loads(f.read())
    except FileNotFoundError:
        return None


def get_last_year_processed():
    source = get_sourcejson()
    if not source:
        return YEAR_INIT
    years = list(map(int, source.keys()))
    years.sort()
    return years[-1:][0]


def get_last_month_processed():
    source = get_sourcejson()
    if not source:
        return 1
    try:
        months = list(map(int, source[str(get_last_year_processed())]["months"].keys()))
    except KeyError:
        return 1
    months.sort()
    last = months[-1:][0]
    return last if last < 12 else 1


def save(rates, year, month):
    year_path = os.path.join(DATA_DIR, year)
    month_path = os.path.join(year_path, month)
    for date in rates.keys():
        day_path = os.path.join(month_path, date.split('-')[2])
        distutils.dir_util.mkpath(day_path)
        d = {date: rates[date]}
        with open(os.path.join(day_path, "rates.json"), "w") as f:
            f.write(json.dumps(d, cls=DecimalEncoder))


def run():
    new_source = get_years()
    current_source = get_sourcejson()
    if current_source:
        for year in new_source.keys():
            for month in new_source[year]["months"]:
                current_source[year]["months"][month] = new_source[year]["months"][
                    month
                ]
                rates = get_rates(
                    new_source[year]["months"][month]["link"], year, month
                )
                save(rates, year, month)
    update_sourcejson(current_source)
