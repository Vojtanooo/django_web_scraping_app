import requests
from bs4 import BeautifulSoup


def bazos_data(psc, distance):
    bazos_url = f"https://reality.bazos.cz/prodam/pozemek/?hlokalita={psc}&humkreis={distance}"
    session = requests.Session().get(bazos_url).text
    html = BeautifulSoup(session, "html.parser")

    pages_list = []
    pages_list.append(bazos_url)

    if html.find("div", class_="strankovani"):
        other_pages = html.find("div", class_="strankovani").findAll("a")
        for item in other_pages:
            other_page = item.get("href", "")
            pages_list.append(f"https://reality.bazos.cz{other_page}")
        pages_list.pop()

    scrape_list = []
    scrape_list_items = []
    for page in pages_list:
        session = requests.Session().get(page).text
        html = BeautifulSoup(session, "html.parser")
        village_name = html.findAll("div", class_="inzeraty")
        for scrape in village_name:
            name = scrape.find("span", class_="nadpis").text
            description = scrape.find("div", class_="popis").text
            if "prodej stavebního pozemku" in name.lower() or "prodej stavebního pozemku" in description.lower():
                scrape_list_items.append(scrape)
            elif "k výstavbě rodinného domu" in name.lower() or "k výstavbě rodinného domu" in description.lower():
                scrape_list_items.append(scrape)
            elif "stavební pozemek" in name.lower() or "stavební pozemek" in description.lower():
                scrape_list_items.append(scrape)
            elif "pozemky pro bydlení" in name.lower() or "pozemky pro bydlení" in description.lower():
                scrape_list_items.append(scrape)

    for item in scrape_list_items:
        price = item.find("div", class_="inzeratycena").text
        if item.find("img", class_="obrazek"):
            img_url = item.find("img", class_="obrazek").get("src", "")
        else:
            img_url = "Žádný obrázek"
        info = item.find("span", class_="nadpis").text
        url = item.find("a").get("href", "")
        scrape_dict = {
            "price": price,
            "img_url": img_url,
            "info": info,
            "url": f"https://reality.bazos.cz{url}"
        }
        scrape_list.append(scrape_dict)
    return scrape_list
