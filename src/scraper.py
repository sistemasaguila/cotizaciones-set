import re

import distutils.dir_util
import json
import os
from datetime import date
from decimal import Decimal

from utils import DecimalEncoder, get_soup, normalize


MONTHS = {
    "Enero": "01",
    "Febrero": "02",
    "Marzo": "03",
    "Abril": "04",
    "Mayo": "05",
    "Junio": "06",
    "Julio": "07",
    "Agosto": "08",
    "Septiembre": "09", # 🤦
    "Setiembre": "09",  # 🤦
    "Octubre": "10",
    "Noviembre": "11",
    "Diciembre": "12",
}

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
SOURCEJSON_URL = os.path.join(BASE_DIR, "source.json")
YEAR_INIT = 2014
CURRENT_YEAR = date.today().strftime("%Y")
CURRENT_MONTH = date.today().strftime("%m")
BASE_URL = "https://www.set.gov.py"
URL = f"{BASE_URL}/web/portal-institucional/cotizaciones"


def get_sections():
    sections = {}
    soup = get_soup(URL)
    if soup:
        for section in soup.select("[data-analytics-asset-title]"):
            pattern = r"(\b[A-Za-z]+)\s+(\d{4})\b"
            section_text = section.attrs.get("data-analytics-asset-title", "")
            result = re.search(pattern, section_text)
            if result:
                month_str = result.group(1)
                year = int(result.group(2))
                month = MONTHS[month_str]
                
                if year >= YEAR_INIT and year >= get_last_year_processed():
                    year_str = str(year)
                    sections[year_str] = sections.get(year_str, {})
                    sections[year_str][month] = section.select("table")

        for year in sections.keys():
            sections[year] = dict(sorted(sections[year].items(), key=lambda x: x[0]))                    

    return sections


def get_rates(soup, year="2022", month="03"):
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
    date = None
    if soup:
        table = soup[0]
        tbody = table.select("tbody")[0]
        rows = tbody.select("tr")
        for row in rows:
            cols = row.select("td")
            # Removing extra columns without data:
            # like https://www.set.gov.py/portal/PARAGUAY-SET/detail?folder-id=repository:collaboration:/sites/PARAGUAY-SET/categories/SET/Informes%20Periodicos/cotizaciones-historicos/2016/h-mes-de-agosto&content-id=/repository/collaboration/sites/PARAGUAY-SET/documents/informes-periodicos/cotizaciones/2016/H_-_Mes_de_Agosto
            cols = [c for c in cols if len(c.getText().strip()) > 0]
            for k, col in enumerate(cols):
                text = col.getText()
                if k in scheme["day"]["cols"]:
                    date = f"{year}-{month}-{'{:0>2}'.format(text.strip())}"
                else:
                    currency = [x for x in scheme.keys() if k in scheme[x]["cols"]][0]
                    value = Decimal(normalize(text.strip()))
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
        return {}


def get_yearjson(url):
    try:
        with open(url, "r") as f:
            return json.loads(f.read())
    except FileNotFoundError:
        return {}


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
    latest = None
    year_path = os.path.join(DATA_DIR, year)
    month_path = os.path.join(year_path, month)
    for date in rates.keys():
        day_path = os.path.join(month_path, date.split("-")[2])
        distutils.dir_util.mkpath(day_path)
        latest = {date: rates[date]}
        with open(os.path.join(day_path, "rates.json"), "w") as f:
            f.write(json.dumps(latest, cls=DecimalEncoder))

    with open(os.path.join(month_path, "rates.json"), "w") as f:
        f.write(json.dumps(rates, cls=DecimalEncoder))

    yearjson = get_yearjson(os.path.join(year_path, "rates.json"))
    yearjson = dict(yearjson, **rates)
    with open(os.path.join(year_path, "rates.json"), "w") as f:
        f.write(json.dumps(yearjson, cls=DecimalEncoder))
        
    if latest:
        with open(os.path.join(DATA_DIR, "latest.json"), "w") as f:
            f.write(json.dumps(latest, cls=DecimalEncoder))


def run():
    new_source = get_sections()
    current_source = get_sourcejson()
    for year in new_source.keys():
        if current_source.get(year, None) is None:
            current_source[year] = {"months": {"01": {"link": None}}}
        for month in new_source[year].keys():
            current_source[year]["months"][month] = {"link": URL}
            rates = get_rates(new_source[year][month], year, month)
            save(rates, year, month)
    
    update_sourcejson(current_source)
