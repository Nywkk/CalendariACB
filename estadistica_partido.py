from bs4 import BeautifulSoup
import requests
from datetime import datetime
import arrow


def extract_time(href):
    url = "https://www.acb.com"+href
    result = requests.get(url)
    # Parse the HTML content
    soup = BeautifulSoup(result.text, 'html.parser')

    #Find the time placed in the div
    time_place = soup.find("div", class_='datos_evento roboto texto-centrado colorweb_4 bg_azul_medio').text
    time_place_split = time_place.split()
    time_original = time_place_split[0] +" "+time_place_split[2]
    time = datetime.strptime(time_original, "%d/%m/%Y %H:%M")
    fecha_hora_iso8601 = time.strftime("%Y-%m-%dT%H:%M:%S")
    return fecha_hora_iso8601


