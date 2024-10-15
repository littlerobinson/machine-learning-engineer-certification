# Databricks notebook source
# MAGIC %md
# MAGIC # Steam's videogames platform 👾
# MAGIC
# MAGIC ## Projet 🚧
# MAGIC
# MAGIC Vous travaillez pour Ubisoft, un éditeur français de jeux vidéo. Ils souhaitent sortir un nouveau jeu vidéo révolutionnaire ! Ils vous ont demandé de réaliser une analyse globale des jeux disponibles sur la place de marché de Steam afin de mieux comprendre l'écosystème vidéoludique et les tendances actuelles.
# MAGIC
# MAGIC ## 1. Analyse exploratrice

# COMMAND ----------

# Imports
from pyspark.sql import functions as F
from pyspark.sql.types import IntegerType, StringType, ArrayType
from pyspark.sql.functions import unix_timestamp, from_unixtime

import pandas as pd


# COMMAND ----------

# Récupérer le fichier avec les datas en tant que datframe et afficher le schéma
FILEPATH = 's3://full-stack-bigdata-datasets/Big_Data/Project_Steam/steam_game_output.json'

raw_data = spark.read.json(FILEPATH)

raw_data.printSchema()

# COMMAND ----------

# Afficher la forme du dataframe
shape = (raw_data.count(), len(raw_data.columns))
display(shape)

# COMMAND ----------

raw_data.describe()

# COMMAND ----------

# MAGIC %md
# MAGIC Il y a 55691 `id` dans le dataframe.

# COMMAND ----------

df_ids = raw_data.select('id').limit(5)
display(df_ids)

# COMMAND ----------

# Afficher la forme du dataframe pour l index data
steam_data = raw_data.select('data')
display(steam_data)

# COMMAND ----------

# MAGIC %md
# MAGIC On peut voir que toutes les informations sont dans une donnée `json` stockée dans la colonne `data`. 
# MAGIC Il y a même dans ce json l'`id` avec la clé `appid`.
# MAGIC
# MAGIC ### Sélection des données

# COMMAND ----------

steam_data.printSchema()

# COMMAND ----------

steam_data_flat = steam_data.select(
    F.col("data.*"),
)

display(steam_data_flat)


# COMMAND ----------

# Compter le nombre d'occurences différentes par colonne
def count_distinct_values(df):
    distinct_counts = []
    for column in df.columns:
        distinct_count = df.select(column).distinct().count()
        distinct_counts.append((column, distinct_count))
    return distinct_counts

distinct_counts = count_distinct_values(steam_data_flat)
# Créer un DataFrame avec les résultats
schema = ["column_name", "count"]
distinct_value_count_df = spark.createDataFrame(distinct_counts, schema)
display(distinct_value_count_df)

# COMMAND ----------

# Exploration colonne Type où il n'y a que 2 valeurs
# Visualiser la liste des valeurs différentes pour la colonne type
type_counts_df = steam_data_flat.groupBy("type").count()
display(type_counts_df)

# COMMAND ----------

# Exploration du jeu ayant le type hardware pour vérifier si c'est une vealuer
hardware_df = steam_data_flat.filter(F.col('type') == 'hardware')
display(hardware_df)

# COMMAND ----------

# Ce n'est pas un jeu mais une application pour streamer ses jeux sur différents types d'appareils
# Suppression de la ligne
steam_data_flat = steam_data_flat.filter(F.col('type') != 'hardware')

# COMMAND ----------

# Choisir la liste des données à garder
from enum import Enum

class Status(Enum):
  NOT_SELECTED = 'not selected'
  SELECTED = 'selected'
  LATER = 'later'
  MAYBE = 'maybe'

selection_dict = {
'appid': Status.SELECTED,
'categories': Status.SELECTED,
'ccu': Status.NOT_SELECTED,
'developer': Status.SELECTED,
'discount': Status.SELECTED,
'genre': Status.SELECTED,
'header_image': Status.NOT_SELECTED,
'initialprice': Status.SELECTED,
'languages': Status.SELECTED,
'name': Status.SELECTED,
'negative': Status.SELECTED,
'owners': Status.SELECTED,
'platforms': Status.SELECTED,
'positive': Status.SELECTED,
'price': Status.SELECTED,
'publisher': Status.SELECTED,
'release_date': Status.SELECTED,
'required_age': Status.SELECTED,
'short_description': Status.NOT_SELECTED,
'tags': Status.MAYBE,
'type': Status.NOT_SELECTED,
'website': Status.NOT_SELECTED,
'release_date': Status.SELECTED
}



selection_df = pd.DataFrame.from_dict({k: v.value for k, v in selection_dict.items()},
                                      orient='index', columns=['status'])
selection_df




# COMMAND ----------

selection_df \
  .groupby('status') \
  .agg({'status': 'count'}) \
  .rename(columns={'status': 'count'})

# COMMAND ----------

selected_columns = list(selection_df.loc[selection_df['status'] == "selected"].index)
selected_columns

# COMMAND ----------

display(steam_data_flat)

# COMMAND ----------

steam_data_selected = steam_data_flat.select(selected_columns)
display(steam_data_selected)

# COMMAND ----------

# MAGIC %md
# MAGIC ### Nettoyage des données

# COMMAND ----------

# Mettre la date au format date
steam_data_selected = steam_data_selected.withColumn("release_date_timestamp", F.to_timestamp(F.col("release_date"), format="y/M/d"))
display(steam_data_selected)

# COMMAND ----------

# Contrôle des colonnes contennant des valeurs numériques
numeric_cols = ['discount', 'initialprice', 'negative', 'positive', 'price', 'required_age']
steam_data_numeric = steam_data_selected.select(numeric_cols)
steam_data_numeric_desc = steam_data_numeric.describe()
display(steam_data_numeric_desc)

# COMMAND ----------

# vérifications du type des colonnes
steam_data_numeric.dtypes

# COMMAND ----------

# MAGIC %md
# MAGIC Il n'y a pas de valeurs négatives mais par contres l faut vérifier 2 choses :
# MAGIC - la colonne required_age ne comprend pas seulement que des valeurs entières.
# MAGIC - A voir si les prix à 0 sont normaux. jeux gratuits ?
# MAGIC - Les colonnes sont en chaine de caractères et non en numérique.

# COMMAND ----------

# Cast des colonnes prix
steam_data_selected = steam_data_selected \
                .withColumn('initialprice', steam_data_selected['initialprice'].cast(IntegerType())) \
                .withColumn('price', steam_data_selected['price'].cast(IntegerType())) \
                .withColumn('discount', steam_data_selected['discount'].cast(IntegerType()))

# COMMAND ----------

# Contrôle des colonnes contennant des valeurs numériques
numeric_cols = ['discount', 'initialprice', 'negative', 'positive', 'price', 'required_age']
steam_data_numeric = steam_data_selected.select(numeric_cols)
steam_data_numeric_desc = steam_data_numeric.describe()
display(steam_data_numeric_desc)

# COMMAND ----------

steam_data_numeric.dtypes

# COMMAND ----------

# Nettoyage de la colonne required_age
required_age_df = steam_data_selected.groupBy(F.col('required_age')).count().orderBy('required_age', ascending=True)
display(required_age_df)

# COMMAND ----------

# MAGIC %md
# MAGIC Les valeurs `required_age` à nettoyer sont :
# MAGIC - 7+
# MAGIC - 21+
# MAGIC - MA 15+
# MAGIC
# MAGIC Autre point d'attention, certaines valeurs ne sont pas très cohérentes :
# MAGIC - 180 --> est ce 18 avec un 0 en plus, jeux russes à priori
# MAGIC - 35 --> Je n'ai pas trop d'idée

# COMMAND ----------

from pyspark.sql.functions import col, when

# remplacement des valeurs non numériques
df_cleaned = required_age_df.withColumn(
    "required_age",
    when(col("required_age").rlike("^[0-9]+$"), col("required_age").cast("int"))  # Cas où `required_age` est un nombre
    .when(col("required_age").rlike("7\\+"), 7)  # Cas où `required_age` est "7+"
    .when(col("required_age").rlike("21\\+"), 21)  # Cas où `required_age` est "21+"
    .when(col("required_age").rlike("MA 15"), 15)  # Cas où `required_age` est "MA 15"
    .otherwise(0)  # Valeur par défaut pour les autres cas, vous pouvez remplacer `0` par autre chose si nécessaire
)

#required_age_clean_df = df_cleaned.groupBy(F.col('required_age')).agg(F.count("*").alias("count"))
required_age_clean_df = df_cleaned.select("required_age").distinct().orderBy('required_age')

display(required_age_clean_df)

# COMMAND ----------

# clean du dataframe des jeux
from pyspark.sql.functions import col, when

# remplacement des valeurs non numériques
steam_data_selected = steam_data_selected.withColumn(
    "required_age",
    when(col("required_age").rlike("^[0-9]+$"), col("required_age").cast("int"))  # Cas où `required_age` est un nombre + cast en entier
    .when(col("required_age").rlike("7\\+"), 7)  # Cas où `required_age` est "7+"
    .when(col("required_age").rlike("21\\+"), 21)  # Cas où `required_age` est "21+"
    .when(col("required_age").rlike("MA 15"), 15)  # Cas où `required_age` est "MA 15"
)

# COMMAND ----------

# Sélection des jeux dont `required_age` est supérieur à 21.

weird_ages_games_df = steam_data_selected.filter(col('required_age') > 20)
display(weird_ages_games_df.select(col('developer'), col('genre'), col('languages'), col('name'), col('required_age')))

# COMMAND ----------

# MAGIC %md
# MAGIC Au vu des jeux et pour être en concordance avec les réglementations en France je vais modifier l'age requis de ces jeux par 18.

# COMMAND ----------

steam_data_selected = steam_data_selected.withColumn(
    "required_age",
    when(col("required_age") > 20, 18) \
    .otherwise(col("required_age"))
)

# COMMAND ----------

# MAGIC %md
# MAGIC Vérification des données dans les colonnes si par exemple vide ou null.

# COMMAND ----------

# Liste des colonnes avec des valeurs nulles
columns_with_nulls = [c for c in selected_columns if steam_data_selected.filter(F.col(c).isNull()).count() > 0]

# Afficher les colonnes contenant des valeurs nulles
print("Colonnes avec des valeurs nulles : ", columns_with_nulls)

# COMMAND ----------

# Liste des colonnes avec des valeurs vides
string_cols = ['developer', 'genre', 'languages', 'name', 'publisher']

columns_with_empty_values = [
    c for c in string_cols if steam_data_selected.filter((F.length(F.trim(F.col(c))) == 0)).count() > 0
]
# Afficher les colonnes contenant des valeurs vides
print("Colonnes avec des valeurs vides : ", columns_with_empty_values)

# COMMAND ----------

# MAGIC %md
# MAGIC ***ATTENTION***, dans les recherche qui suivent il faudra prendre en compte qu'il y a des valeurs nulles et des valeurs vides.

# COMMAND ----------

# MAGIC %md
# MAGIC ## Analyse
# MAGIC
# MAGIC ### Analyse Macro
# MAGIC
# MAGIC #### Which publisher has released the most games on Steam?
# MAGIC
# MAGIC Pour répondre à cette question il suffit de regrouper les jeux via la colonne `publisher` et de compter le nombre d'occurences.

# COMMAND ----------

# Nettoyage de la colonne publisher pour éviter les espaces en trop
steam_data_selected = steam_data_selected.withColumn("publisher", F.trim(steam_data_selected.publisher))

# COMMAND ----------

# Créer une vue temporaire pour les catégories
# Attention la colonne publisher contient des valeurs vides, ne pas les prendre en compte
steam_data_selected.createOrReplaceTempView("steam_view")

# Regroupement par publisher avec les publishers les plus importants en premier
# et dans la valeur publisher est renseignée
publishers_df = spark.sql("""
    SELECT publisher, COUNT(*) as game_count
    FROM steam_view
    WHERE publisher != ''
    GROUP BY publisher
    ORDER BY game_count DESC
    LIMIT 10
""")

display(publishers_df)


# COMMAND ----------

# MAGIC %md
# MAGIC #### What are the best rated games?
# MAGIC
# MAGIC Pour répondre à cette question nous avons 2 colonnes intéressantes :
# MAGIC - `positive` qui a l'air d'être le nombre d'avis positifs sur le jeux
# MAGIC - `negative` qui a l'air d'être le nombre d'avis négatifs sur le jeux
# MAGIC
# MAGIC A voir mais peut être créer une pondération en fonction du nombre de votes. Certains jeux ont des milliers de votes alors que d'autres en ont moins que 10.

# COMMAND ----------

# Création d'un dataframe avec les données qui nous intéressent ordonnées par le plus de notes positives
rated_games_df = steam_data_selected.select(col('name'), col('publisher'), col('positive'), col('negative'))
rated_games_df = rated_games_df.withColumn('total_votes', col('positive') + col('negative')) \
                                .withColumn('average_rating', col('positive') / col('total_votes')) \
                                .withColumn('ratio', col('positive') / col('negative')) \
                                .orderBy('positive', ascending=False)
display(rated_games_df)

# COMMAND ----------

# Statistiques
pd.set_option('display.float_format', lambda x: '%.2f' % x)
rated_games_stats_df = rated_games_df.select(col('total_votes'), col('positive'), col('negative'), col('ratio')).toPandas().describe()
rated_games_stats_df

# COMMAND ----------

# MAGIC %md
# MAGIC Nous pouvons voir que l'écart type est important entre des `petits` jeux ayant peu de votes et des jeux AAA ayant énormémont de votes.

# COMMAND ----------

# MAGIC %md
# MAGIC ##### Bayesian Average
# MAGIC La note moyenne pondérée, également connue sous le nom de Bayesian Average, est une méthode utilisée pour évaluer des objets (comme des jeux vidéo) qui ont des nombres de votes très différents. Elle permet de donner une note plus équitable en tenant compte de la quantité de votes reçus par chaque objet.
# MAGIC
# MAGIC Imaginons deux jeux :
# MAGIC
# MAGIC     Jeu A a une note moyenne de 4.5 étoiles basée sur 2 votes.
# MAGIC     Jeu B a une note moyenne de 4.2 étoiles basée sur 500 votes.
# MAGIC
# MAGIC Même si la note moyenne brute de Jeu A est plus élevée, il a reçu beaucoup moins de votes, ce qui le rend moins fiable. La note moyenne pondérée ajuste ces notes pour compenser les différences dans le nombre de votes.
# MAGIC Comment ça fonctionne ?
# MAGIC
# MAGIC     Moyenne globale des votes positifs (C) :
# MAGIC     C'est la moyenne de tous les votes positifs pour tous les jeux. Par exemple, si tous les jeux combinés ont une moyenne de 80% de votes positifs, alors C = 0.80.
# MAGIC
# MAGIC     Seuil de votes (m) :
# MAGIC     C'est une valeur choisie pour déterminer combien de votes sont nécessaires pour que la note d'un jeu commence à être considérée comme fiable. Souvent, on utilise un chiffre basé sur la distribution des votes, comme le 75ème percentile des votes totaux. Par exemple, m=145m=145.
# MAGIC
# MAGIC     Note moyenne du jeu (R) :
# MAGIC     C'est la note moyenne brute du jeu, calculée en divisant le nombre de votes positifs par le nombre total de votes. Par exemple, si un jeu a 100 votes positifs et 200 votes totaux, alors R=100200=0.50R=200100​=0.50.
# MAGIC
# MAGIC     Nombre de votes (v) :
# MAGIC     C'est le nombre total de votes pour le jeu.
# MAGIC

# COMMAND ----------

# Création d'une vue pour utiliser les requêtes sql
rated_games_df.createOrReplaceTempView("rated_games")

# Méthode utilisée: Note moyenne pondérée (Bayesian Average)

m = 145  # choix de m en prenant le 75ème percentile du nombre total de vote. Plus cette valeur est haute plus les grands jeux ressortiront

# Requête de récupération des données permettant de calculer la moyenne globale de votes positifs
total_votes_query = spark.sql("""
    SELECT 
        SUM(total_votes) AS sum_total_votes,
        SUM(positive) AS sum_positive
    FROM rated_games
    ORDER BY sum_total_votes DESC
    """)

# moyenne globale des votes positifs
x = total_votes_query.collect()[0]['sum_positive'] / total_votes_query.collect()[0]['sum_total_votes']

# Création du dataframe avec la pondération utilisant la statistique bayésienne
weighted_rated_games_df = spark.sql(f"""
    SELECT *,
        ({x} * {m} + total_votes * (positive / total_votes)) / ({m} + total_votes) as bayesian_average
    FROM rated_games
    ORDER BY bayesian_average DESC
    LIMIT 100
""")

# Affichage
display(weighted_rated_games_df)

# COMMAND ----------

# MAGIC %md
# MAGIC #### Are there years with more releases? Were there more or fewer game releases during the Covid, for example?

# COMMAND ----------

# Création d'un dataframe avec les données qui nous intéressent avec une nouvelle représentant l'année de sortie
releases_over_years_df = steam_data_selected.select(col('name'), col('publisher'), col('release_date'), F.year('release_date_timestamp').alias('year'))
releases_over_years_df.show(10)

# COMMAND ----------

# Calcul du nombre de sorties par an sur la plateforme steam
count_release_over_years_df = releases_over_years_df.groupBy('year').count().orderBy('count', ascending=False)
display(count_release_over_years_df)

# COMMAND ----------

# Vérification de la date des derniers jeux sorties dans cette base de données
releases_over_years_df.filter(col('year') > 2021).orderBy(col('release_date'), ascending=False).show()

# COMMAND ----------

# MAGIC %md
# MAGIC Nous pouvons voir que nous avons un pic de sorties de jeux vidéos en 2021. 
# MAGIC Il y a une baisse sur 2022 dû au fait que la base de données s'arrête le 7 novembre 2022.
# MAGIC Il y a une très légère baisse en 2019, peut être d^au covid mais sans aucune certitude vu qu'en cette année, seulement la Chine était vraiment impacté.

# COMMAND ----------

# MAGIC %md
# MAGIC #### How are the prizes distributed? Are there many games with a discount?

# COMMAND ----------

# Création d'un dataframe avec les données qui nous intéressent
games_prices_df = steam_data_selected.select(col('name'), col('publisher'), col('initialprice'), col('price'), col('discount'), F.year('release_date_timestamp').alias('year'))
games_prices_df.show(10)

# COMMAND ----------

# Statistiques sur les prix
prices_cols = ['initialprice', 'price', 'discount']
steam_data_prices_desc = games_prices_df.select(prices_cols).toPandas().describe(percentiles=[0.25, 0.50, 0.75, 0.90])
steam_data_prices_desc

# COMMAND ----------

# Compage du nombre de discount dans la base de données
games_prices_df.select(col('discount')).filter(col('discount') > 0).count()

# COMMAND ----------

# Regroupement des jeux ayant des discount par année de sortie
discount_over_year_df = games_prices_df.filter(col('discount') > 0).groupBy('year').count().orderBy(col('year'), ascending=False)
display(discount_over_year_df)

# COMMAND ----------

# MAGIC %md
# MAGIC Il y a seulement 2518 jeux bénéficiant d'une réduction sur la plateforme ce qui est assez peu sur 55690 jeux.
# MAGIC On peut aussi voir que ce sont plutôt les jeux des dernières années qui ont des remises.

# COMMAND ----------

# Quel sont les jeux lex plus chères
most_expansive_steam_games = games_prices_df.filter(col('price') > 10000).orderBy(col('price'), ascending=False)
display(most_expansive_steam_games)

# COMMAND ----------

# MAGIC %md
# MAGIC #### What are the most represented languages?

# COMMAND ----------

# Récupérations de toutes les langues disponibles dans les jeux

# utilisation de split pour transformer la chaines de caractères en list et explode pour démultiplier les lignes via chaucune de ces valeurs
games_languages_df = steam_data_selected.withColumn("language", F.explode(F.split(steam_data_selected["languages"], ",")))
display(games_languages_df)

# COMMAND ----------

# Visualisation de tous les languages présent sur la plateforme steam
distinct_languages_df = games_languages_df.groupBy('language').count().orderBy('count', ascending=False)
display(distinct_languages_df)

# COMMAND ----------

from pyspark.sql.functions import trim, when, col

# Un nettoyage est nécessaire
games_languages_cleaned_df = games_languages_df \
    .withColumn(
                "language", # transformation des valeurs si contiennent une de ces valeurs
                when(col("language").rlike("(?i).*Chinese.*"), "Chinese") \
                .when(col("language").rlike("(?i).*Spanish.*"), "Spanish") \
                .when(col("language").rlike("(?i).*Portuguese.*"), "Portuguese") \
                .when(col("language").rlike("(?i).*English.*"), "English") \
                .when(col("language").rlike("(?i).*German.*"), "German") \
                .when(col("language").rlike("(?i).*Italian.*"), "Italian") \
                .when(col("language").rlike("(?i).*Japanese.*"), "Japanese") \
                .when(col("language").rlike("(?i).*French.*"), "French") \
                .when(col("language").rlike("(?i).*Russian.*"), "Russian") \
                .when(col("language").rlike("(?i).*Korean.*"), "Korean") \
                .otherwise(trim(col("language")))
    ).filter(col("language") != "") # Pas de valeur vide non plus

distinct_languages_df = games_languages_cleaned_df.groupBy('language').count().orderBy('count', ascending=False)
display(distinct_languages_df)


# COMMAND ----------

# Résultat des 10 languages les plus utilisés

display(distinct_languages_df.limit(10))

# COMMAND ----------

# MAGIC %md
# MAGIC #### Are there many games prohibited for children under 16/18?

# COMMAND ----------

# Récupérations de tous les ages requis dans les jeux déjà fait dans la partie nettoyage des données

display(required_age_clean_df)

# COMMAND ----------

prohibited_games_df = steam_data_selected.select(col('name'), col('genre'), col('publisher'), col('required_age'), col('release_date')).filter(col('required_age') > 15)
display(prohibited_games_df)

# COMMAND ----------

prohibited_games_df.count()

# COMMAND ----------

# MAGIC %md
# MAGIC Il y a 306 jeux dont l'âge requis est de 16 ans et plus.

# COMMAND ----------

# MAGIC %md
# MAGIC ### Genres analysis
# MAGIC
# MAGIC #### What are the most represented genres?

# COMMAND ----------

# Création d'un dataframe avce les données voulus
from pyspark.sql.functions import split

# Il faut splitter la colonne genre car il peut y avoir plusieurs genre pour un jeu, séparé par une virgule
games_genres_df = steam_data_selected.select(col('appid'), col('name'), col('publisher'), F.explode(split(col('genre'), ',')).alias('uniq_genre'), F.year('release_date_timestamp').alias('year'))
display(games_genres_df)

# COMMAND ----------

games_genres_stats = games_genres_df.select(col('uniq_genre')).groupBy('uniq_genre').count().orderBy(col('count'), ascending=False).limit(10)
display(games_genres_stats)

# COMMAND ----------

# MAGIC %md
# MAGIC Ce sont les jeux indépendants qui ont le plus de jeux sur steam.

# COMMAND ----------

# MAGIC %md
# MAGIC #### Are there any genres that have a better positive/negative review ratio?
# MAGIC

# COMMAND ----------

# récupération des données voulu et nettoyage des espaces avant et après.
games_genres_notes_df = steam_data_selected.select(col('appid'), col('name'), col('publisher'), F.explode(split(col('genre'), ',')).alias('uniq_genre'), F.year('release_date_timestamp').alias('year'), (col('positive')/col('negative')).alias('note_ratio'))

# Nettoyer la colonne uniq_genre en supprimant les espaces
games_genres_notes_df = games_genres_notes_df.withColumn('uniq_genre', trim(games_genres_notes_df['uniq_genre']))

display(games_genres_notes_df)

# COMMAND ----------

# Vérification de la colonne genre nettoyée
uniq_genre_count_df = games_genres_notes_df.select(col('uniq_genre')).groupBy(col('uniq_genre')).count().orderBy(col('uniq_genre'))
display(uniq_genre_count_df)

# COMMAND ----------

# Suppression des jeux sans genre, nous n'en avons pas besoin, ils représentent partie infimes des jeux
uniq_genre_count_df = uniq_genre_count_df.filter(uniq_genre_count_df['uniq_genre'] != '')
display(uniq_genre_count_df)

# COMMAND ----------

from pyspark.sql.functions import avg

avg_note_best_ratio_df = games_genres_notes_df.groupBy('uniq_genre').agg(avg(col('note_ratio')).alias('avg_note_ratio')).orderBy(col('avg_note_ratio'), ascending=False).limit(5)
display(avg_note_best_ratio_df)

# COMMAND ----------

avg_note_worst_ratio_df = games_genres_notes_df.groupBy('uniq_genre').agg(avg(col('note_ratio')).alias('avg_note_ratio')).orderBy(col('avg_note_ratio'), ascending=True).limit(5)
display(avg_note_worst_ratio_df)

# COMMAND ----------

# MAGIC %md
# MAGIC #### Do some publishers have favorite genres?
# MAGIC

# COMMAND ----------

from pyspark.sql.functions import countDistinct

# Compter le nombre de genres par publisher
genre_count_df = games_genres_notes_df.groupBy("publisher").agg(countDistinct("uniq_genre").alias("genre_count"))

display(genre_count_df)

# COMMAND ----------

# Filtrer les publishers qui ont exactement un genre
single_genre_publishers = genre_count_df.filter(genre_count_df["genre_count"] == 1)

print(f"Il y a {single_genre_publishers.count()} éditeurs avec seulement 1 seul genre.")


# COMMAND ----------

# Filtrer les publishers qui ont plusieurs genres
multiple_genre_publishers = genre_count_df.filter(genre_count_df["genre_count"] > 1)

print(f"Il y a {multiple_genre_publishers.count()} éditeurs avec plusieurs genres de jeux.")

# COMMAND ----------

# MAGIC %md
# MAGIC Au vu des chiffres ont peut dire que la majorité des éditeurs ont plus d'un genre de jeu (environ 89.2%). Sachant qu'il est possible de mettre plusieurs genres pour le même jeu cela est peu étonnant.

# COMMAND ----------

# MAGIC %md
# MAGIC #### What are the most lucrative genres?

# COMMAND ----------

# récupération des données voulu et nettoyage des espaces avant et après.
games_genres_notes_df = steam_data_selected.select(col('appid'), col('name'), F.explode(split(col('genre'), ',')).alias('uniq_genre'), col('price'), col('owners'))

# Nettoyer la colonne uniq_genre en supprimant les espaces
games_genres_prices_df = games_genres_notes_df.withColumn('uniq_genre', trim(games_genres_notes_df['uniq_genre']))

display(games_genres_prices_df)

# COMMAND ----------

from numpy import median
from pyspark.sql.functions import udf
from pyspark.sql.types import IntegerType

# Fonction pour récupérer la valeur médiane d'une liste d'entiers
def calculate_median(range_str):
    min_val, max_val = [int(x.replace(",", "").strip()) for x in range_str.split("..")]
    return int(median([min_val, max_val]))

# Définir l'UDF pour appliquer la fonction calculate_median
# Les fonctions UDF (User Defined Functions) en PySpark sont des fonctions définies par l'utilisateur qui permettent d'appliquer des transformations personnalisées sur les colonnes d'un DataFrame.
median_udf = udf(calculate_median, IntegerType())

# Ajouter une nouvelle colonne avec la médiane des fourchettes
games_genres_prices_df = games_genres_prices_df.withColumn("owners_median", median_udf(col("owners")))

# Affichage
display(games_genres_prices_df)

# COMMAND ----------

# Afficher des statistiques descriptives de la colonne owners_median, vérification des valeurs
owners_median_desc = games_genres_prices_df.describe("owners_median")
display(owners_median_desc)

# COMMAND ----------

# Meilleurs ventes de jeux par genres
top_sales_games = games_genres_prices_df.orderBy(col('owners_median'), ascending=False).limit(10)

# COMMAND ----------

# Calcul de la somme des nombres de ventes par genre
from pyspark.sql.functions import sum

total_owners_for_genre_df = games_genres_prices_df.groupBy(col('uniq_genre')).agg(sum("owners_median").alias("total_owners")).orderBy(col('total_owners'), ascending=False).limit(10)

display(total_owners_for_genre_df)

# COMMAND ----------

# MAGIC %md
# MAGIC Cela nous donne une valeur approximative car nous n'avons pas la variation des prix dans le temps et les jeux peuvent appartenir à plusieurs genres en même temps. 
# MAGIC Le top 3 des ventes de jeux sont Action, Indie et Adventure.

# COMMAND ----------

# MAGIC %md
# MAGIC #### What are the most represented tags? (personnal question)

# COMMAND ----------

# Création d'un dataframe avec les données voulus
games_categories_df = steam_data_selected.select(col('appid'), col('name'), col('publisher'), F.explode(steam_data_selected.categories).alias("category"), col('genre'), col('initialprice'), F.year('release_date_timestamp').alias('year'))

display(games_categories_df)


# COMMAND ----------

games_categories_stats = games_categories_df.select(col('category')).groupBy('category').count().orderBy(col('count'), ascending=False).limit(10)
display(games_categories_stats)

# COMMAND ----------

# MAGIC %md
# MAGIC ### Platform analysis

# COMMAND ----------

# MAGIC %md
# MAGIC #### Are most games available on Windows/Mac/Linux instead?

# COMMAND ----------

# Création d'un dataframe avec les données qui nous intéressent
# Extraire les colonnes linux, mac, et windows de la colonne platforms
game_platforms_df = steam_data_selected \
       .withColumn("platforms_linux", F.col("platforms.linux")) \
       .withColumn("platforms_mac", F.col("platforms.mac")) \
       .withColumn("platforms_windows", F.col("platforms.windows"))

# Supprimer la colonne originale platforms
game_platforms_df = game_platforms_df.drop("platforms")

# Sélection des colonnes
selected_game_platforms_df = game_platforms_df.select(col('name'), col('publisher'), col('genre'), col('platforms_windows'), col('platforms_mac'), col('platforms_linux'))

display(selected_game_platforms_df)

# COMMAND ----------

# Compter le nombre de jeux par plateforme
platform_count_df = selected_game_platforms_df.select(
    (col("platforms_windows").cast("int")).alias("windows_count"),
    (col("platforms_mac").cast("int")).alias("mac_count"),
    (col("platforms_linux").cast("int")).alias("linux_count")
).agg(
    sum("windows_count").alias("windows_count"),
    sum("mac_count").alias("mac_count"),
    sum("linux_count").alias("linux_count")
).withColumn(
    "total_count",
    col("windows_count") + col("mac_count") + col("linux_count")
)

display(platform_count_df)

# COMMAND ----------

# MAGIC %md
# MAGIC #### Do certain genres tend to be preferentially available on certain platforms?

# COMMAND ----------

# Récupération des données voulu et nettoyage des espaces avant et après.
games_platforms_df = selected_game_platforms_df.withColumn('uniq_genre', F.explode(split(col('genre'), ',')).alias('uniq_genre'))

# Nettoyer la colonne uniq_genre en supprimant les espaces
games_platforms_df = games_platforms_df.withColumn('uniq_genre', trim(games_platforms_df['uniq_genre']))

# Compter le nombre de jeux par genre et plateforme
platform_genre_count_df = games_platforms_df.groupBy("uniq_genre").agg(
    sum(col("platforms_windows").cast("int")).alias("windows_count"),
    sum(col("platforms_mac").cast("int")).alias("mac_count"),
    sum(col("platforms_linux").cast("int")).alias("linux_count")
).orderBy(col('linux_count'), ascending=False)

# Afficher les résultats
display(platform_genre_count_df)

# COMMAND ----------

# MAGIC %md
# MAGIC La plupart des jeux sont présents sur Windows mais on peut voir que les jeux indépendants sont les jeux qui sont les plus présents sur les 3 plateformes à la fois.
