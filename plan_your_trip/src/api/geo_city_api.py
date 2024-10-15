import os
from dotenv import load_dotenv
import logging
import requests
import requests_cache
import json
import pandas as pd
import numpy as np
from io import StringIO
from urllib.parse import quote

load_dotenv()

logger = logging.getLogger(__name__)

# Configuring the cache for requests
requests_cache.install_cache('geo_city_api_cache', expire_after=int(os.environ['NOMINATIM_CACHE_EXPIRATION']))

class GeoCityApi:

    headers = {} 

    def __init__(self):
        """Initialization of GeoCityApi"""
        logger.info('GeoCityApi initialization')
        self.headers = {
                'Accept-Encoding': 'application/json',
                'User-Agent': 'Chrome/126.0.0.0 ',
            }

    def _api_call(self, city: str, country: str = 'france') -> dict:
        """Performs a synchronous API request to obtain geographic information about a city."""
        encoded_city = quote(city)
        encoded_country = quote(country)
        url = f"https://nominatim.openstreetmap.org/search?format=json&country={encoded_country}&city={encoded_city}"

        response = requests.get(url, headers=self.headers)
        response.raise_for_status()  # Vérifie si la requête a réussi
        return response.json()

    def _get_json_result(self, cities_infos: list) -> str:
        """Converts geographic city information into JSON."""
        response = []
        for city_rows in cities_infos:
            for row in city_rows:
                response.append(row)
        return json.dumps(response)

    def search_cities_geo_infos(self, cities: list, country: str = 'france') -> list:
        """Find geographical information for a list of cities."""
        results = []
        logger.info("Starting query...")
        for city in cities:
            result = self._api_call(city, country)
            results.append(result)
        return results

    def get_clean_dataframe(self, result: list, city_list: list) -> pd.DataFrame:
        """Cleans the data obtained from the API and returns a DataFrame."""
        cities_json = self._get_json_result(result)
        df = pd.read_json(StringIO(cities_json))

        df = df[df['name'].isin(city_list)]
        df = df.loc[:, ['name', 'addresstype', 'lat', 'lon', 'osm_id']]

        priority_order = {'town': 1, 'city': 2, 'municipality': 3, 'village': 4, 'peak': 5, 'historic': 6}
        df['priority'] = df['addresstype'].map(priority_order).fillna(7)
        df.drop(df[df['addresstype'] == 'hamlet'].index, inplace=True)

        df = df.sort_values(by=['name', 'priority'])
        df = df.drop_duplicates(subset=['name'], keep='first')
        df = df.drop(columns=['priority'])
        df = df.reset_index(drop=True)

        # create a new column id
        df['id'] = np.arange(0, len(df))

        return df

    def create_output_result(self, df: pd.DataFrame, file_path: str = 'data/city_geo_infos.csv'):
        """Save DataFrame as CSV."""
        df.to_csv(file_path, index=False)

