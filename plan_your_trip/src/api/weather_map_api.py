import os
from dotenv import load_dotenv
import logging
import requests
import requests_cache
from datetime import datetime
import pandas as pd

load_dotenv()

logger = logging.getLogger(__name__)

# Configuring the cache for requests
requests_cache.install_cache(
    "weather_map_api_cache",
    expire_after=int(os.environ["OPENWEATHERMAP_CACHE_EXPIRATION"]),
)


class WeatherMapApi:
    headers = {}

    url_list = []

    def __init__(self, df: pd.DataFrame):
        """Initialization of"""
        logger.info("WeatherMapApi initialization")
        self.headers = {
            "Accept-Encoding": "application/json",
            "User-Agent": "Chrome/126.0.0.0 ",
        }
        try:
            # check if `lat` and `lon` columns exists
            if "lat" not in df.columns or "lon" not in df.columns:
                raise KeyError(
                    "Columns 'lat' and 'lon' are not present in the DataFrame."
                )
        except KeyError as e:
            logger.error(e)
            return False

        self.input_df = df
        # Feed URLs list with input dataframe who contain longitudes and latitudes data
        self._get_urls()

    def _get_urls(self) -> list:
        """Transform a cities dataframe with a column `lat` and a column `lon` to an URLs list to get weather infos"""
        # Load api key stored in env file
        api_key = os.environ["OPENWEATHERMAP_API"]
        for i in range(len(self.input_df)):
            longitude = self.input_df.loc[i, "lon"]
            latitude = self.input_df.loc[i, "lat"]

            dict_urls = {
                "name": self.input_df.loc[i, "name"],
                "addresstype": self.input_df.loc[i, "addresstype"],
                "city_id": self.input_df.loc[i, "id"],  # get city_id relation
                "url": f"https://api.openweathermap.org/data/3.0/onecall?units=metric&lat={latitude}&lon={longitude}&exclude=minutely,hourly,current&appid={api_key}",
            }
            self.url_list.append(dict_urls)

    def _api_call(self, url: str) -> dict:
        """Performs a synchronous API request to obtain weather ."""
        response = requests.get(url, headers=self.headers)
        return response.json()

    def search_weather_infos(self) -> pd.DataFrame:
        results = []
        logger.info("Starting query...")
        for url_dict in self.url_list:
            meteo_dict = self._api_call(url_dict["url"])
            dict_result = meteo_dict["daily"]
            df_result = pd.DataFrame(
                [
                    {
                        "city_id": url_dict["city_id"],
                        "lat": meteo_dict["lat"],
                        "lon": meteo_dict["lon"],
                        "addresstype": url_dict["addresstype"],
                        "city": url_dict["name"],
                        "dt": datetime.fromtimestamp(hourly_result["dt"]),
                        "summary": hourly_result["summary"],
                        "temp_min": hourly_result["temp"]["min"],
                        "temp_max": hourly_result["temp"]["max"],
                        "temp_day": hourly_result["temp"]["day"],
                        "feels_like_day": hourly_result["feels_like"]["day"],
                        "feels_like_night": hourly_result["feels_like"]["night"],
                        "feels_like_eve": hourly_result["feels_like"]["eve"],
                        "feels_like_morn": hourly_result["feels_like"]["morn"],
                        "humidity": hourly_result["humidity"],
                        "weather_main": hourly_result["weather"][0]["main"],
                        "weather_desc": hourly_result["weather"][0]["description"],
                        "clouds": hourly_result["clouds"],
                        "pop": hourly_result["pop"],
                        "rain": hourly_result.get("rain", None),
                        "uvi": hourly_result["uvi"],
                        "wind_speed": hourly_result["wind_speed"],
                    }
                    for hourly_result in dict_result
                ]
            )
            results.append(df_result)

        # Concat all dataframes in results list in one dataframe
        df_weather_result = pd.concat(results, ignore_index=True)
        return df_weather_result

    def create_output_result(
        self, df: pd.DataFrame, file_path: str = "data/weather_infos.csv"
    ):
        """Save DataFrame as CSV."""
        df.to_csv(file_path, index=False)
