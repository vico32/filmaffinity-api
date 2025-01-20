from flask import Flask, request, jsonify
from config import *
from bs4 import BeautifulSoup
import requests
import re

app = Flask(__name__)

@app.route('/api/search', methods=['GET'])
def search():
    headers = {"user-agent": USER_AGENT}
    query = request.args.get('query')
    if not query:
        msg = {"error": "The query parameter must contain the information to be searched for."}
        return jsonify(msg), STATUS_CODE_ERROR

    url = f'{URL_SEARCH_FILMAFFINITY}{query}'
    res = requests.get(url, headers=headers, timeout=10)

    elements = []
    response = []

    if res.status_code != 200:
        msg = {"error": f"filmaffinity error: {res.status_code}"}
        return jsonify(msg), STATUS_CODE_ERROR
    else:
        # Búsqueda correcta, analizamos los resultados
        elements = web_scrapping_filmaffinity_search_page(res.text)

    if not elements:
        msg = {"error": "Sin resultados"}
        return jsonify(msg), STATUS_CODE_NOT_FOUND

    for element in elements:
        try:
            filmCode = url_to_film_code(element[1])
        except:
            continue

        responseItem = {
            "id": filmCode,
            "api": f'/api/film?id={filmCode}',
            "title": element[0],
            "url": element[1],
            "rating": element[2],
            "year": element[3],
            "image": element[4],
            "genre": element[5],
            "summary": element[6]
        }
        response.append(responseItem)

    return jsonify(response), STATUS_CODE_OK

@app.route('/api/film', methods=['GET'])
def filmById():
    headers = {"user-agent": USER_AGENT}
    urlParameter = request.args.get('url')
    id = request.args.get('id')
    if urlParameter:
        id = url_to_film_code(urlParameter)

    if not id:
        msg = {"error": "The id or url parameter is required. Try /api/search endpoint to obtain the id."}
        return jsonify(msg), STATUS_CODE_ERROR

    url = f'{URL_FILMAFFINITY_FILM_PAGE}{id}.html'
    res = requests.get(url, headers=headers, timeout=10)

    element = []
    response = []

    if res.status_code != 200:
        msg = {"error": f"filmaffinity error: {res.status_code}"}
        return jsonify(msg), STATUS_CODE_ERROR
    else:
        # Búsqueda correcta, analizamos el resultado
        element = web_scrapping_filmaffinity_main_page(res.text)

    response = {
        "id": id,
        "title": element[0],
        "url": element[1],
        "rating": element[2],
        "year": element[3],
        "image": element[4],
        "originalTitle": element[5],
        "country": element[6],
        "director": element[7],
        "genre": element[8],
        "company": element[9],
        "summary": element[10],
        "cast": element[11],
        "credits": element[12],
        "photography": element[13],
        "music": element[14],
        "ratingCount": element[15],
        "duration": element[16]
    }

    return jsonify(response), STATUS_CODE_OK

def web_scrapping_filmaffinity_search_page(htmlText):
    soup = BeautifulSoup(htmlText, "html.parser")
    
    # Depuración: Imprimir el HTML para verificar la estructura
    print(soup.prettify())  # Añadir esto para ver la estructura de la página

    filmaffinityRawElements = soup.find_all(class_='movie-card mc-flex movie-card-1')

    filmaffinityElements = []

    noResults = soup.find('b', string=re.compile(r"No hay resultados?"))

    if noResults:
        return filmaffinityElements
    elif filmaffinityRawElements:  # Hemos ido a la pantalla de búsqueda porque hay más de un resultado
        for filmElement in filmaffinityRawElements:
            posterElement = filmElement.find('div', class_="mc-poster")
            imageElement = posterElement.find('img')
            if imageElement:
                image = imageElement['src'].replace("mtiny", "large")
            else:
                image = None

            linkOnImage = posterElement.find('a')
            url = linkOnImage['href']

            title = linkOnImage['title'].rstrip()

            yearElement = filmElement.find_previous(class_='ye-w')
            year = yearElement.get_text() if yearElement else '-'

            ratingElement = posterElement.find_next(class_='avgrat-box')
            rating = ratingElement.get_text() if ratingElement else '--'

            genreElement = filmElement.find('div', class_="mc-genre")
            genre = genreElement.get_text() if genreElement else "Desconocido"

            # Depuración: Ver cómo estamos extrayendo la sinopsis
            summaryElement = filmElement.find('div', class_="mc-summary")
            summary = summaryElement.get_text().strip() if summaryElement else "Sinopsis no disponible"
            print(f"Summary: {summary}")  # Mostrar la sinopsis extraída para verificar

            filmaffinityElements.append([title, url, rating, year, image, genre, summary])
    else:  # No hemos ido a la pantalla de búsqueda sino a la página de la película/serie en sí
        completeInformation = web_scrapping_filmaffinity_main_page(htmlText)
        filmaffinityElements.append([completeInformation[0], completeInformation[1], completeInformation[2], completeInformation[3], completeInformation[4], completeInformation[8], completeInformation[10]])

    return filmaffinityElements

def web_scrapping_filmaffinity_main_page(htmlText):
    soup = BeautifulSoup(htmlText, "html.parser")
    
    # Title
    title = None
    try:
        title = soup.find('h1').find('span').get_text().strip()
    except:
        title = ""
    
    # URL
    allLinks = soup.find_all('a')
    url = None
    for link in allLinks:
        if 'Ficha' in link.get_text():
            url = link['href']
            break
    
    # Rating
    rating = None
    try:
        rating = soup.find(id="movie-rat-avg").get_text().replace("  ", "").strip()
    except:
        rating = "--"

    # Image
    image = soup.find('a', class_="lightbox")['href']

    dtElements = soup.find_all('dt')
    ddElements = soup.find_all('dd')
    data = {}
    for dt, dd in zip(dtElements, ddElements):
        key = dt.text
        value = dd.text
        data[key] = value

    # Original Title
    originalTitle = None
    try:
        originalTitle = data["Título original"].strip().replace(".", ",")
    except:
        originalTitle = ""

    # Year
    year = None
    try:
        year = data["Año"].strip()
    except:
        year = ""

    # Country
    country = None
    try:
        country = data["País"].strip()
    except:
        country = ""

    # Directors
    director = None
    try:
        director = data["Dirección"].strip()
    except:
        director = ""

    # Genre
    genre = None
    try:
        genre = re.sub(r'\s+', ' ', re.sub(r'\s*\|\s*', '. ', data["Género"])).strip()
    except:
        genre = ""

    # Company
    company = None
    try:
        company = data["Compañías"].strip()
    except:
        company = ""

    # Summary
    summary = None
    try:
        summary = data["Sinopsis"].strip()
    except:
        summary = ""

    # Cast
    cast = None
    try:
        castElement = soup.find('dd', class_="card-cast-debug")
        castArray = castElement.find_all('a')
        names = [a.get('title') for a in castArray if a.get('title')]
        cast = ", ".join(names)
    except:
        cast = ""

    # Credits
    credits = None
    try:
        credits = data["Guion"].strip()
    except:
        credits = ""

    # Photography
    photography = None
    try:
        photography = data["Fotografía"].strip()
    except:
        photography = ""

    # Music
    music = None
    try:
        music = data["Música"].strip()
    except:
        music = ""

    # Rating count
    ratingCount = None
    try:
        ratingCountElement = soup.find(id="movie-count-rat")
        ratingCount = ratingCountElement.find('span')['content']
    except:
        ratingCount = "0"

    # Duration
    duration = None
    try:
        duration = data["Duración"].strip().replace(".", "")
    except:
        duration = ""

    return [title, url, rating, year, image, originalTitle, country, director, genre, company, summary, cast, credits, photography, music, ratingCount, duration]

def url_to_film_code(url):
    match = re.search(r"\/film(\d+)", url)
    if match:
        return match.group(1)
    return None

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=22049, debug=True)
