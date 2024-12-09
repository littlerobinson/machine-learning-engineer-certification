import os
import time
import logging
from pathlib import Path
from scrapy.crawler import CrawlerProcess
import requests
import pandas as pd
import json
from io import StringIO
from dotenv import load_dotenv

load_dotenv()

from src.api import geo_city_api
from src.api import weather_map_api
from src.scraping import booking_spyder
from src.infrastructure import datalake_s3
from src.infrastructure import datawarehouse_rds
from src.db import forecast_processor, accomodation_processor

# Logging configuration
logging.basicConfig(
    format="%(asctime)s %(levelname)s: %(message)s",
    level=os.environ.get("LOG_LEVEL", "WARNING"),
)
logger = logging.getLogger(__name__)

# Cities where search for forecast and hotels
city_list = [
    "Mont Saint-Michel",
    "Saint-Malo",
    "Bayeux",
    "Le Havre",
    "Rouen",
    "Paris",
    "Amiens",
    "Lille",
    "Strasbourg",
    "Château du Haut-Kœnigsbourg",
    "Colmar",
    "Eguisheim",
    "Besançon",
    "Dijon",
    "Annecy",
    "Grenoble",
    "Lyon",
    "Gorges du Verdon",
    "Bormes-les-Mimosas",
    "Cassis",
    "Marseille",
    "Aix-en-Provence",
    "Avignon",
    "Uzès",
    "Nîmes",
    "Aigues-Morte",
    "Saintes-Maries-de-la-Mer",
    "Collioure",
    "Carcassonne",
    "Ariège",
    "Toulouse",
    "Montauban",
    "Biarritz",
    "Bayonne",
    "La Rochelle",
    "Gap",
    "Briançon",
]

# Process crawls scrappy
process = CrawlerProcess(
    settings={
        "USER_AGENT": "Chrome/126.0.0.0",
        "LOG_LEVEL": logging.WARNING,
        "REQUEST_FINGERPRINTER_IMPLEMENTATION": "2.7",
        "AUTOTHROTTLE_ENABLED": True,
        "HTTPCACHE_ENABLED": True,
        "HTTPCACHE_DIR": "httpcache",
        "HTTPCACHE_EXPIRATION_SECS": 3600,  # Cache d'une heure
        "RETRY_TIMES": 3,  # Retry 3 times
        "FEEDS": {
            str(os.environ.get("OUTPUT_PATH_BOOKING")): {
                "format": "json",
                "indent": 4,
            }
        },
    }
)

if __name__ == "__main__":
    # # ======================================================================
    # # Fetch cities geo info from API https://nominatim.org
    # # ======================================================================

    # # Instanciate API class
    # gc_api = geo_city_api.GeoCityApi()
    # start = time.time()
    # # Récupération des informations géographiques des villes
    # city_infos = gc_api.search_cities_geo_infos(city_list, "france")
    # end = time.time()
    # elapsed = str(end - start)
    # logger.info("The process took {} seconds to get cities infos.".format(elapsed))

    # # ======================================================================
    # # Data cleaning
    # # ======================================================================

    # cleaned_city_df = gc_api.get_clean_dataframe(city_infos, city_list)
    # logger.info(cleaned_city_df)

    # # ======================================================================
    # # Save cleaned data in a CSV file
    # # ======================================================================

    # gc_api.create_output_result(cleaned_city_df, "data/city_geo_infos.csv")

    # # ======================================================================
    # # Get list of city where geo_city_api find results
    # # id for relationnal table and name to search when scraping
    # # ======================================================================

    # existing_cities_name = cleaned_city_df[["name", "id"]]
    # existing_cities_list_dict = existing_cities_name.to_dict(orient="records")

    # # ======================================================================
    # # Fetch forecast of this cities from API
    # # https://api.openweathermap.org/data/3.0/onecall
    # # ======================================================================

    # wm_api = weather_map_api.WeatherMapApi(cleaned_city_df)
    # start = time.time()
    # weather_df = wm_api.search_weather_infos()
    # end = time.time()
    # elapsed = str(end - start)
    # logger.info("The process took {} seconds".format(elapsed))

    # print("The process took {} seconds".format(elapsed))  # 3 seconds
    # # Save DataFrame as CSV to check content
    # wm_api.create_output_result(weather_df, "data/weather_infos.csv")

    # # ======================================================================
    # # Scraping
    # # ======================================================================

    # # Delete file name if existing
    # booking_file = Path(os.environ.get("OUTPUT_PATH_BOOKING"))
    # if booking_file.is_file():
    #     os.remove(booking_file)

    # # Start the crawling process by passing the cities names where search
    # try:
    #     process.crawl(booking_spyder.BookingSpider, cities=existing_cities_list_dict)
    #     process.start()
    # except Exception as e:
    #     raise SystemExit(e)

    # # ======================================================================
    # # Putting data on AWS S3 Datalake
    # # ======================================================================
    # try:
    #     dls3 = datalake_s3.DataLakeS3()
    #     dls3.connect(bucket_name=os.environ["AWS_BUCKET_NAME"])
    #     dls3.upload_from_dir(s3_dir=os.environ["AWS_PROJECT_PATH"])
    # except Exception as e:
    #     raise SystemExit(e)

    # ======================================================================
    # Clean data and transfer data to data warehouse
    # ======================================================================
    try:
        dw_rds = datawarehouse_rds.DataWarehouseRDS()

        # df_list_csv, df_list_json = dw_rds.get_dataframes_from_s3_dir(
        #     bucket_name=os.environ["AWS_BUCKET_NAME"],
        #     s3_dir=os.environ["AWS_PROJECT_PATH"],
        # )
        # print(df_list_csv)
        # print(df_list_json)

        city_geo_df = dw_rds.read_csv_from_s3(
            bucket_name=os.environ["AWS_BUCKET_NAME"],
            key=os.environ["AWS_PROJECT_PATH"] + "/city_geo_infos.csv",
        )
        city_geo_df = dw_rds.clean_and_save_city_df(city_geo_df)
        print(city_geo_df)

        forecast_df = dw_rds.read_csv_from_s3(
            bucket_name=os.environ["AWS_BUCKET_NAME"],
            key=os.environ["AWS_PROJECT_PATH"] + "/weather_infos.csv",
        )
        forecast_df = dw_rds.clean_and_save_forecast_df(forecast_df)
        print(forecast_df)

        accomodation_df = dw_rds.read_json_from_s3(
            bucket_name=os.environ["AWS_BUCKET_NAME"],
            key=os.environ["AWS_PROJECT_PATH"] + "/booking_results.json",
        )
        accomodation_df = dw_rds.clean_and_save_accomodation_df(accomodation_df)
        print(accomodation_df)

    except Exception as e:
        raise SystemExit(e)

    # ======================================================================
    # Data viz with plotly bubble map to display Top French destinations with forecast
    # ======================================================================

    try:
        processor = forecast_processor.ForecastProcessor()
        forecast_fig = processor.generator_bubble_map()
    except Exception as e:
        raise SystemExit(e)

    try:
        processor = accomodation_processor.AccomodationProcessor()
        accomodation_fig = processor.generator_bubble_map()
    except Exception as e:
        raise SystemExit(e)

    # Put figures in an html page
    forecast_fig_html = forecast_fig.to_html(full_html=False)
    with open("output/forecast.html", "w") as file:
        file.write(forecast_fig_html)

    accomodation_fig_html = accomodation_fig.to_html(full_html=False)
    with open("output/accomodation.html", "w") as file:
        file.write(accomodation_fig_html)
