import numpy as np
import pandas as pd
import plotly.express as px
import plotly.figure_factory as ff
import plotly.graph_objects as go
import streamlit as st
from functions import statistics
from plotly.subplots import make_subplots


#############################################################################
#   Functions
#############################################################################
def get_threshold_slider():
    with st.sidebar:
        # Slider to set delay threshold
        return st.slider(
            "Select delay threshold (in minutes)",
            0,
            THRESHOLD_MINUTE_MAX,
            step=5,
        )


@st.cache_data
def load_delay_analysis_data():
    data = pd.read_excel("./src/data/get_around_delay_analysis.xlsx")
    # Change columns names to lowercase
    data.rename(lambda x: str(x).lower(), axis="columns", inplace=True)
    return data


def group_by_delay(minutes):
    if minutes < 0:
        val = "0. Pas de retard"
    elif minutes < 15:
        val = "1. Retard < 15 min"
    elif minutes < 60:
        val = "2. 15 ≤ Retard < 60 min"
    elif minutes >= 60:
        val = "4. Retard ≥ 60 min"
    return val


def prepare_data(data):
    delay_map = data.set_index("rental_id")["delay_at_checkout_in_minutes"].to_dict()
    data["previous_ended_rental_delay_at_checkout"] = data[
        "previous_ended_rental_id"
    ].apply(lambda x: delay_map.get(x, None))
    data[data["state"] == "canceled"].head(20)

    data["profit"] = data["delay_at_checkout_in_minutes"].apply(
        lambda x: "%.2f" % (x * float(MEDIAN_MINUTE_PRICE))
    )
    data["profit"] = data["profit"].astype(float)
    data["delay"] = (
        data["delay_at_checkout_in_minutes"].dropna().apply(lambda x: group_by_delay(x))
    )
    return data


#############################################################################
#   Global variable
#############################################################################
# Price per minutes for location (calculate in notebook)
MEDIAN_DAY_PRICE = 119
MEDIAN_MINUTE_PRICE = 1.98
THRESHOLD_MINUTE_MAX = 400

#############################################################################
#   IHM
#############################################################################
if __name__ == "__main__":
    st.set_page_config(layout="wide")

    with st.sidebar:
        st.header("🚀 Getaround")

    st.title("🚀 Getaround")

    stats_tab, answers_tab = st.tabs(["stats", "answers"])
    with stats_tab:
        st.header("statistiques")

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

        # Create a text element and let the reader know the data is loading.
        with st.spinner("Loading and 🧪 prepare data..."):
            data = load_delay_analysis_data()
            data = prepare_data(data=data)

        st.markdown("---")
        show_stats = st.checkbox("**Visualiser les statistiques basiques.**")
        if show_stats:
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

            st.markdown("---")

        # Distribution des délais pour la récupération du véhicule
        total_counts = (
            data[data["delay"].notna()]
            .groupby("checkin_type")
            .size()
            .reset_index(name="total_count")
        )
        delay_counts = (
            data[data["delay"].notna()]
            .groupby(["delay", "checkin_type"])
            .size()
            .reset_index(name="count")
        )
        # Fusionner les DataFrames pour obtenir le total_count
        delay_counts = delay_counts.merge(total_counts, on="checkin_type")
        # Calculer le pourcentage de chaque catégorie de délai par checkin_type
        delay_counts["percentage"] = (
            delay_counts["count"] / delay_counts["total_count"]
        ) * 100
        # Créer le graphique à barres côte à côte
        fig = px.bar(
            delay_counts,
            x="delay",
            y="percentage",
            color="checkin_type",
            barmode="group",
            title="Pourcentage des délais par type d'enregistrement",
            labels={
                "delay": "Catégorie de délai",
                "percentage": "Pourcentage",
                "checkin_type": "Type enregistrement",
            },
        )
        fig.update_traces(texttemplate="%{y:.2f}%", textposition="inside")
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")

    with answers_tab:
        # Filter late and canceled rentals
        late_rentals = data[
            (data["delay_at_checkout_in_minutes"] > 0) & (data["state"] == "ended")
        ]
        canceled_rentals = data[data["state"] == "canceled"]

        delay_threshold = get_threshold_slider()

        # Calcul de la perte
        delay_losses = late_rentals[
            late_rentals["delay_at_checkout_in_minutes"] >= delay_threshold
        ]["profit"].sum()

        # Affichage comme s'il y vait 3 colonnes
        col1, _ = st.columns([1, 3])

        with col1:
            st.markdown(
                f"""
                <div style="background-color: #FF4C4B; padding: 10px; border-radius: 5px;">
                    <h3 style="color: white; text-align: center;">Pertes total dû aux retards</h3>
                    <p style="color: white; font-size: 20px; text-align: center;">{delay_losses:.2f} €</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

        # Calculate estimated cost due to delay
        estimated_delay_cost = (
            late_rentals[
                late_rentals["delay_at_checkout_in_minutes"] >= delay_threshold
            ]["delay_at_checkout_in_minutes"].sum()
            * MEDIAN_MINUTE_PRICE
        )

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
