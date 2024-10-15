import os
import pandas as pd
from sqlalchemy import create_engine, text
import plotly.express as px
from src.utils.database_connection import DatabaseConnection

class ForecastProcessor():

    def __init__(self):
        db_instance = DatabaseConnection()
        self.engine = db_instance.get_engine()

    def _fetch_data(self):
        query = text("select  f.city_id, f.city, f.lat, f.lon, \
                        avg(f.feels_like_day) as feels_temperature_day, \
                        avg(f.forecast_score) as score_mean, \
                        avg(f.humidity) as humidity_mean, \
                        avg(f.wind_speed) as wind_mean, \
                        avg(f.pop) as prob_rain_mean \
                        from forecasts f \
                        group by f.city_id, f.city, f.lat, f.lon \
                        order by score_mean desc, f.city asc \
                        limit 5")

        df = pd.read_sql(query, self.engine)
        return df

    def generator_bubble_map(self):
        """Fetch data from database and generate plotly buuble map"""
        df = self._fetch_data()

        # Get prob rain value in percentage
        df['prob_rain_percentage'] = df['prob_rain_mean'] * 100

        # Créer la carte de type "bubble" avec Plotly Express
        fig = px.scatter_mapbox(
            df,
            lat="lat",
            lon="lon",
            hover_name="city",
            hover_data={
                'lat': False,
                'lon': False,
                'city': True,
                'feels_temperature_day': True,
                'score_mean': False,
                'humidity_mean': True,
                'wind_mean': True,
                'prob_rain_mean': False,
                'prob_rain_percentage': True,
                },
            color="feels_temperature_day", 
            size="score_mean",
            size_max=30,  # Taille maximale des bulles
            zoom=5,  # Niveau de zoom initial de la carte
            mapbox_style="carto-positron",
        )

        # Configurer le style de la carte
        fig.update_layout(
            title_x=0.5,
            title_text='The 5 cities with the best weather over the next 8 days'
        )

        return fig

