from django.shortcuts import redirect, render
from django.core.paginator import Paginator
from django.contrib import messages
import requests
from bs4 import BeautifulSoup
from requests.sessions import session
from unidecode import unidecode
from .models import Search
from .scrape_data import bazos_data, idnes_data


def home(request):
    if request.method == "POST":
        psc = request.POST.get("psc")
        distance = request.POST.get("select_field")
        choice = request.POST.get("group1")

        if distance == None:
            distance = "0"
            distance_to_html = "+0km"
        elif distance == "2":
            distance_to_html = "+1km"
        elif distance == "3":
            distance_to_html = "+5km"
        elif distance == "4":
            distance_to_html = "+10km"
        elif distance == "5":
            distance_to_html = "+20km"

        distance_bazos = distance_to_html.strip("+ km")

        psc_url = f"https://www.psc.cz/{psc}/"
        session = requests.Session().get(psc_url).text
        html = BeautifulSoup(session, "html.parser")
        if html.find("div", class_="psc-text").h1.text == "":
            messages.error(request, f"Nesprávně zadané PSČ!")
            return redirect("home")
        else:
            village_name = html.find(
                "div", class_="psc-text").h1.text.split(",")[1]

        if " u " in village_name:
            raw_village_name = village_name.split(" u ")[0].lower().strip(" ")
        else:
            raw_village_name = unidecode(village_name).strip(
                " ").replace(" ", "-").lower()

        district = html.findAll("span", itemprop="name")[2].text
        district_unidecode = unidecode(district).replace(" ", "-").lower()
        district_for_search = raw_village_name + "-" + district_unidecode

        if choice == "land":
            choice = "Pozemky na prodej "
            idnes_url = f"https://reality.idnes.cz/s/prodej/pozemky/stavebni-pozemek/{district_for_search}/?s-rd={distance}"
            bazos_url = f"https://reality.bazos.cz/prodam/pozemek/?hlokalita={psc}&humkreis={distance_bazos}"
        elif choice == "house":
            choice = "Domy na prodej "
            idnes_url = f"https://reality.idnes.cz/s/prodej/domy/{district_for_search}/?s-rd={distance}"
            bazos_url = f"https://reality.bazos.cz/prodam/dum/?hlokalita={psc}&humkreis={distance_bazos}"
        else:
            choice = "Byty na prodej "
            idnes_url = f"https://reality.idnes.cz/s/prodej/byty/{district_for_search}/?s-rd={distance}"
            bazos_url = f"https://reality.bazos.cz/prodam/byt/?hlokalita={psc}&humkreis={distance_bazos}"

        scrape_list = []
        scrape_list.extend(idnes_data(idnes_url))
        scrape_list.extend(bazos_data(bazos_url))

        search_results = f"{len(scrape_list)} inzerátů"

        if len(scrape_list) == 0:
            messages.error(request, "Žádné reality v oblasti!")

        paginator = Paginator(scrape_list, 12)
        page_num = request.GET.get("page", 1)
        page = paginator.page(page_num)

        request.session["pagination"] = scrape_list
        request.session["distance"] = distance_to_html
        request.session["village_name"] = village_name
        request.session["choice"] = choice
        request.session["search_results"] = search_results

        Search.objects.create(
            psc=psc, distance=distance_to_html, choice=choice)

        return render(request, "home.html", {
            "village_name": village_name,
            "distance": distance_to_html,
            "choice": choice,
            "scrape_list": page,
            "search_results": search_results,
            "page_obj": page
        })

    elif request.method == "GET":
        if "pagination" in request.session:
            paginator = Paginator(request.session.get("pagination"), 12)
            page_num = request.GET.get("page", 1)
            page = paginator.page(page_num)

            return render(request, "home.html", {
                "village_name": request.session.get("village_name"),
                "distance": request.session.get("distance"),
                "choice": request.session.get("choice"),
                "scrape_list": page,
                "search_results": request.session.get("search_results"),
                "page_obj": page
            })
    return render(request, "home.html")


def delete_session(request):
    request.session.flush()
    return render(request, "home.html")
