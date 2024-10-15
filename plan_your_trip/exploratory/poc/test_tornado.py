# test avec la librairie tornado

import pandas as pd
import asyncio
import time
import logging
import requests
import json
from io import StringIO
from tornado.httpclient import AsyncHTTPClient
from urllib.parse import quote

# Configuration du logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

reduced_city_list = [
"Toulouse",
"Montauban",
"Biarritz",
"Bayonne",
"La Rochelle",
"Gap",
"Briançon",
"Chateau du Haut Koenigsbourg"
]

city_list = [
"Mont Saint Michel",
"St Malo",
"Bayeux",
"Le Havre",
"Rouen",
"Paris",
"Amiens",
"Lille",
"Strasbourg",
"Chateau du Haut Koenigsbourg",
"Colmar",
"Eguisheim",
"Besancon",
"Dijon",
"Annecy",
"Grenoble",
"Lyon",
"Gorges du Verdon",
"Bormes les Mimosas",
"Cassis",
"Marseille",
"Aix en Provence",
"Avignon",
"Uzes",
"Nimes",
"Aigues Mortes",
"Saintes Maries de la mer",
"Collioure",
"Carcassonne",
"Ariege",
"Toulouse",
"Montauban",
"Biarritz",
"Bayonne",
"La Rochelle",
"Gap",
"Briançon"
]

headers = {
  'Accept-Encoding': 'application/json',
  'User-Agent': 'Chrome/126.0.0.0 ',
}


async def API_call(client, city, country):
    # encode city string to be compatible in url
    encoded_city = quote(city)
    encoded_country = quote(country)

    # url = f"https://nominatim.openstreetmap.org/search?format=json&country={encoded_country}&city={encoded_city}"
    url = f"https://nominatim.openstreetmap.org/search?format=json&q={encoded_city}"
    
    r = await client.fetch(url, method="GET", headers=headers)
    print('request:', url)
    return json.loads(r.body.decode())

async def search_cities_geo_infos(cities, country = 'france'):
    client = AsyncHTTPClient()
    logger.info("Starting query...")
    # create async tasks
    tasks = [asyncio.create_task(API_call(client, city, country)) for city in cities]
    # return result
    return await asyncio.gather(*tasks)

def get_json_result(cities_infos):
    response = []
    for city_rows in cities_infos:
        for row in city_rows:
            response.append(row)
    return json.dumps(response)
    



if __name__ == "__main__":
    start = time.time()
    result = asyncio.run(search_cities_geo_infos(city_list))
    end = time.time()
    elapsed = str(end - start)
    logger.info("The process took {} seconds".format(elapsed))

    print("The process took {} seconds".format(elapsed))

    # Convertir le résultat en JSON
    cities_json = get_json_result(result)
    
    # Créer un DataFrame à partir des résultats
    df = pd.read_json(StringIO(cities_json))

    # filtrage sur le nom des villes pour vérifier s'ils sont exactement égales à la liste des villes en entrée (MONTAUBAN != MONTAUBAN LUCHON)
    df = df[df['name'].isin(city_list)]

    # Filrage sur les colonnes intéressantes
    df = df.loc[:, ['name', 'addresstype', 'lat', 'lon', 'osm_id']]

    # Filtre sur la colonne `addresstype`, nous voulons les villes où `addresstype` == city|town|municipality
    # Définir l'ordre de priorité pour la colonne 'addresstype'
    priority_order = {'municipality': 1, 'town': 2, 'city': 3}
    df.loc[:, 'priority'] = df['addresstype'].map(priority_order).fillna(4) # La méthode fillna(4) est utilisée pour remplir les valeurs manquantes (NaN) dans la colonne priority avec le nombre 4

    # Trier les données en fonction du 'name' et de la priorité
    df = df.sort_values(by=['name', 'priority'])

    # Supprimer les doublons en gardant la première occurrence
    df = df.drop_duplicates(subset=['name'], keep='first')

    # Supprimer la colonne 'priority' qui n'est plus nécessaire
    df = df.drop(columns=['priority'])

    # Sauvegarder le DataFrame en CSV pour vérifier le contenu
    df.to_csv('city_geo_infos.csv', index=False)