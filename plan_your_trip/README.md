Voici un exemple de fichier `README.md` pour votre projet :

---

# Projet de Scrapping et de Prévisions Météo

## Description

Ce projet a pour objectif de récupérer des informations géographiques, des prévisions météorologiques et des données hôtelières pour une liste de villes en France. Les données sont collectées à l'aide de différentes API et de techniques de scrapping web, puis stockées dans un DataLake sur AWS S3 et enfin mise au propre dans un DataWarehouse.
En sortie 2 cartes sont présentées avec le Top des destinations en fonction de la météo et le Top des hôtels dans la région.

## Installation

### Prérequis

- Python 3.8 ou supérieur
- Pip (gestionnaire de paquets Python)
- Un compte AWS avec un bucket S3
- Clés d'API pour [OpenWeatherMap](https://openweathermap.org/api) pour le oncallapi. Gratuit jusqu'à 1000 requêtes par jour.

### Étapes

1. Clonez le dépôt :

    ```bash
    git clone git@github.com:littlerobinson/jedha_plan_your_trip.git
    cd jedha_plan_your_trip
    ```

2. Créez et activez un environnement virtuel :

    ```bash
    python -m venv env
    source env/bin/activate  # Sur Windows, utilisez `env\Scripts\activate`
    ```

3. Installez les dépendances :

    ```bash
    pip install -r requirements.txt
    ```

4. Configurez les variables d'environnement en créant un fichier `.env` à la racine du projet avec les clés et configurations nécessaires :

    ```plaintext
    # Logging
    LOG_LEVEL=

    # AWS
    AWS_ACCESS_KEY_ID=
    AWS_SECRET_ACCESS_KEY=

    # DATABASES
    DB_USERNAME=
    DB_PASSWORD=
    DB_HOSTNAME=
    DB_NAME=
    DB_PORT=

    # API
    OPENWEATHERMAP_API=

    # Scrapping
    OUTPUT_PATH_BOOKING='output/booking_results.json'
    ```

## Utilisation

### Lancement du Script Principal

Pour exécuter le script principal, utilisez la commande suivante :

```bash
python main.py
```

Le script effectuera les opérations suivantes :

1. Récupération des informations géographiques des villes via l'API Nominatim.
2. Récupération des prévisions météorologiques des 8 prochains jours via l'API OpenWeatherMap.
3. Scrapping des données hôtelières sur le site booking.com à l'aide de Scrapy.
4. Chargement des données sur un bucket S3 sur AWS.
5. Nettoyage des données dans une base de donneées AWS RDS.
6. Génération de fichier html avec les cartes des 5 villes où il faut aller en fonction des prévisions météo et des hôtels associés ces villes.

### Configuration de Scrapy

Le script utilise Scrapy pour scrapper les données hôtelières. Les paramètres de configuration de Scrapy sont définis dans le fichier `main.py` sous la section `CrawlerProcess`.

### Gestion des Fichiers

- Les informations géographiques des villes sont stockées dans `output/city_geo_infos.csv`.
- Les informations géographiques des villes sont stockées dans `output/weather_infos.csv`.
- Les données de scrapping des hôtels sont stockées dans `output/booking_data.json`.
- Les fichiers de cache de Scrapy sont stockés dans le répertoire `scrappy/httpcache`.
- Utilisation du cache http pour limiter les appels aux APIs

### Chargement des Données sur AWS S3

Le script se connecte à AWS S3 et charge les fichiers générés dans un bucket spécifié. Assurez-vous de configurer correctement vos clés AWS dans le fichier `.env`.

## Structure du Projet

```
.
├── data
│   ├── booking_results.json
│   ├── city_geo_infos.csv
│   └── weather_infos.csv
├── exploratory
│   ├── kayak_db.png
│   ├── notebook.ipynb
│   ├── poc
│   │   ├── __init__.py
│   │   ├── test_asyncio.py
│   │   ├── test_tornado.py
│   │   ├── write_read_rds.py
│   │   └── write_read_s3.py
│   └── weather_infos.csv
├── LICENSE
├── main.py
├── output
│   ├── accomodation.html
│   └── forecast.html
├── README.md
├── requirements.txt
├── src
│   ├── api
│   │   ├── geo_city_api.py
│   │   └── weather_map_api.py
│   ├── db
│   │   ├── accomodation_processor.py
│   │   ├── forecast_processor.py
│   ├── infrastructure
│   │   ├── datalake_s3.py
│   │   ├── datawarehouse_rds.py
│   ├── scrapping
│   │   ├── booking_spyder.py
│   └── utils
│       ├── database_connection.py
|
└── geo_city_api_cache.sqlite
└── weather_map_api_cache.sqlite
```

## Contribuer

Les contributions sont les bienvenues ! Pour proposer une nouvelle fonctionnalité ou signaler un bug, veuillez ouvrir une issue ou soumettre une pull request.

## Auteurs

- [Alexandre André](https://github.com/littlerobinson)

## Licence

Ce projet est sous licence MIT. Voir le fichier [LICENSE](LICENSE) pour plus de détails.

---

Assurez-vous de remplacer les sections appropriées par vos informations et ajustez les détails si nécessaire.
