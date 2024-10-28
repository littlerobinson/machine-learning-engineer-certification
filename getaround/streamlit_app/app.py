import numpy as np
import pandas as pd
import streamlit as st
from src.components import sidebar
from src.functions import statistics

st.set_page_config(layout="wide")

st.title("🚀 Getaround")

st.markdown(
    """
GetAround est le Airbnb des voitures. Vous pouvez louer des voitures à n'importe qui pour quelques heures ou quelques jours ! Fondée en 2009, cette entreprise a connu une croissance rapide. En 2019, elle compte plus de 5 millions d'utilisateurs et environ 20 000 voitures disponibles dans le monde.

En tant que partenaire de Jedha, ils ont proposé de grands défis :

Pour cette étude de cas, nous vous suggérons de vous mettre à notre place et d'exécuter une analyse que nous avons réalisée en 2017 🔮 🪄

En utilisant Getaround, les conducteurs réservent des voitures pour une durée déterminée, allant d'une heure à plusieurs jours. Ils sont censés rendre la voiture à temps, mais il arrive parfois que les conducteurs soient en retard pour la restitution.

Les retours tardifs à la caisse peuvent générer de fortes frictions pour le conducteur suivant si la voiture était censée être relouée le même jour : le service client signale souvent des utilisateurs insatisfaits car ils ont dû attendre le retour de la voiture de la location précédente ou des utilisateurs qui ont même dû annuler leur location car la voiture n'a pas été restituée à temps.

**Objectifs** 🎯

Afin de limiter ces problèmes, nous avons décidé de mettre en place un délai minimum entre deux locations. Une voiture ne sera pas affichée dans les résultats de recherche si les heures d'arrivée ou de départ demandées sont trop proches d'une location déjà réservée.

Cela résout le problème du retard de paiement, mais nuit également potentiellement aux revenus de Getaround/des propriétaires : nous devons trouver le bon compromis.
    """
)

sidebar.show_sidebar("🚀 Getaround")


@st.cache_data
def load_delay_analysis_data():
    data = pd.read_excel("data/get_around_delay_analysis.xlsx")
    # Change columns names to lowercase
    data.rename(lambda x: str(x).lower(), axis="columns", inplace=True)
    return data


# Create a text element and let the reader know the data is loading.
with st.spinner("Loading data..."):
    data = load_delay_analysis_data()

st.markdown("## 1. Analyse Exploratoire des Données")

st.markdown("**Données bruts:**")

st.write(data)

st.markdown("**Statistiques:**")

stats = statistics.get_basics_statitics(data=data)
for stat in stats.values():
    st.markdown(
        f"**{stat[0]}**",
    )
    st.write(stat[1])


st.markdown("## 2. Questions")


st.markdown("### 2.1. Quelle doit être la durée minimale du délai ?")
st.markdown(
    "### 2.2. Devrions-nous activer la fonctionnalité pour toutes les voitures ou uniquement pour les voitures connectées ?"
)
st.markdown(
    "### 2.3. Quelle part des revenus de notre propriétaire serait potentiellement affectée par cette fonctionnalité ?"
)
st.markdown(
    "### 2.4. Combien de locations seraient affectées par la fonctionnalité en fonction du seuil et de la portée que nous choisissons ?"
)
st.markdown(
    "### 2.5. À quelle fréquence les conducteurs sont-ils en retard pour le prochain contrôle technique ? Quel est l'impact sur le conducteur suivant ?"
)
st.markdown(
    "### 2.6. Combien de cas problématiques cela permettra-t-il de résoudre en fonction du seuil et de la portée choisis ?"
)
