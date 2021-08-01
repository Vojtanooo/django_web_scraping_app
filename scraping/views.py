from django.shortcuts import redirect, render
import requests
from bs4 import BeautifulSoup


def home(request):
    if request.method == "POST":
        psc = request.POST.get("psc")
        distance = request.POST.get("select_field")
        choice = request.POST.get("group1")

        if choice == "land":
            choice = "Pozemky"
        elif choice == "house":
            choice = "Domy"
        else:
            choice = "Byty"

        psc_url = f"https://www.psc.cz/{psc}/"
        session = requests.Session().get(psc_url).text
        html = BeautifulSoup(session, "html.parser")
        village_name = html.find(
            "div", class_="psc-text").h1.text.split(",")[1]
        

        return render(request, "home.html", {"village_name": village_name, "distance": distance, "choice": choice})

    return render(request, "home.html")
