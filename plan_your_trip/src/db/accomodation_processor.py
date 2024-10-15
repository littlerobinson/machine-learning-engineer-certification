import os
import pandas as pd
from sqlalchemy import create_engine, text
import plotly.express as px
from src.utils.database_connection import DatabaseConnection

class AccomodationProcessor():

    def __init__(self):
        db_instance = DatabaseConnection()
        self.engine = db_instance.get_engine()

    def _fetch_data(self, ):
        query = text("select * from accomodations a \
                    where a.city_id in (0, 28, 4, 35, 14) and a.score is not null \
                    order by a.city_id asc, a.score desc")
        df = pd.read_sql(query, self.engine)
        return df

    def generator_bubble_map(self):
        """Fetch data from database and generate plotly buuble map"""
        df = self._fetch_data()

        # Remplacer les virgules par des points
        df['score'] = df['score'].str.replace(',', '.')

        # Convertir la colonne score en float
        df['score'] = df['score'].astype(float)

        # Créer la carte de type "bubble" avec Plotly Express
        fig = px.scatter_mapbox(
            df,
            lat="lat", 
            lon="lon",
            hover_name="name",
            hover_data={
                'lat': False,
                'lon': False,
                'name': True,
                'score': True,
                'description': True,
                },
            color="score", 
            size="score",
            size_max=30,  # Taille maximale des bulles
            zoom=5,  # Niveau de zoom initial de la carte
            mapbox_style="carto-positron",
        )

        # Configurer le style de la carte
        fig.update_layout(
            title_x=0.5,
            title_text='The accomodation in the 5 cities with the best weather over the next 8 days'
        )

        return fig
