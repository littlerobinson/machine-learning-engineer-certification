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


# @st.cache_data
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
        val = "3. Retard ≥ 60 min"
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

    data["rental_count"] = data.groupby("car_id")["car_id"].transform("count")

    data["critical_delay_for_next_rental_in_minutes"] = (
        data["time_delta_with_previous_rental_in_minutes"]
        - data["previous_ended_rental_delay_at_checkout"]
    )

    # Create a column to mark delays causing potential financial losses
    filtered_dataset = data[(data["delay_at_checkout_in_minutes"].notna())]
    data["is_potential_loss_due_to_delay"] = data["delay_at_checkout_in_minutes"].apply(
        lambda x: True if x > 0 else False,
    )

    filtered_dataset = data[(data["previous_ended_rental_delay_at_checkout"].notna())]
    data["is_cancel_due_to_delay_by_previous_rental"] = filtered_dataset[
        "critical_delay_for_next_rental_in_minutes"
    ].apply(lambda x: True if x < 0 else False)

    return data


def delay_distribution_viz(data):
    fig = make_subplots(
        rows=1,
        cols=2,
        subplot_titles=(
            "Checkout delay (min)",
            "Delay with previous rental (min)",
        ),
    )
    fig.add_trace(
        go.Box(
            y=data["delay_at_checkout_in_minutes"],
            name="Checkout delay",
        ),
        row=1,
        col=1,
    )
    fig.add_trace(
        go.Box(
            y=data["time_delta_with_previous_rental_in_minutes"],
            name="Previous rental delay",
        ),
        row=1,
        col=2,
    )
    return fig


def impact_delay_threshold_on_total_loss_viz(data, delay_range=range(0, 800, 50)):
    loss_values = []
    for delay in delay_range:
        adjusted_losses = data["delay_at_checkout_in_minutes"].apply(
            lambda x: (x - delay) * MEDIAN_MINUTE_PRICE if (x - delay) > 0 else 0
        )
        total_loss = adjusted_losses.sum()
        loss_values.append(total_loss)

    loss_data = pd.DataFrame(
        {
            "delay_threshold_between_rentals": delay_range,
            "total_loss": loss_values,
        }
    )
    fig = px.line(
        loss_data,
        x="delay_threshold_between_rentals",
        y="total_loss",
        title="Impact du seuil de retard sur la perte totale",
        labels={
            "delay_threshold_between_rentals": "Seuil de délai entre les locations (minutes)",
            "total_loss": "Perte total ($)",
        },
    )
    return fig


def checkin_type_checkout_delay_viz(dataset):
    fig = make_subplots(rows=1, cols=2, subplot_titles=("Mobile", "Connect"))
    fig.add_trace(
        go.Histogram(
            x=dataset[dataset["checkin_type"] == "mobile"][
                "delay_at_checkout_in_minutes"
            ],
            xbins=dict(  # recentrage
                start=-500, end=500, size=5
            ),
            name="Mobile",
            marker_color="blue",
        ),
        row=1,
        col=1,
    )

    fig.add_trace(
        go.Histogram(
            x=dataset[dataset["checkin_type"] == "connect"][
                "delay_at_checkout_in_minutes"
            ],
            xbins=dict(  # recentrage
                start=-500, end=500, size=5
            ),
            name="Connect",
            marker_color="orange",
        ),
        row=1,
        col=2,
    )

    fig.add_shape(
        type="line",
        x0=0,
        x1=0,
        y0=0,
        y1=600,
        line=dict(color="red", dash="dash"),
        row=1,
        col=1,
    )

    fig.add_shape(
        type="line",
        x0=0,
        x1=0,
        y0=0,
        y1=140,
        line=dict(color="red", dash="dash"),
        row=1,
        col=2,
    )

    fig.update_layout(
        title_text="Distribution des checkout par type d'enregistrement",
        xaxis_title="Délais pour le checkout en minutes",
        yaxis_title="Nombre de checkout",
    )
    return fig


def checkout_by_recovery_times_viz(dataset):
    total_counts = (
        dataset[dataset["delay"].notna()]
        .groupby("checkin_type")
        .size()
        .reset_index(name="total_count")
    )
    delay_counts = (
        dataset[dataset["delay"].notna()]
        .groupby(["delay", "checkin_type"])
        .size()
        .reset_index(name="count")
    )
    delay_counts = delay_counts.merge(total_counts, on="checkin_type")
    delay_counts["percentage"] = (
        delay_counts["count"] / delay_counts["total_count"]
    ) * 100
    fig = px.bar(
        delay_counts,
        x="delay",
        y="percentage",
        color="checkin_type",
        barmode="group",
        title="Répartition des retards par type d'enregistrement",
        labels={
            "delay": "Retard",
            "percentage": "Pourcentage",
            "checkin_type": "Type d'enregistrement",
        },
    )
    fig.update_traces(texttemplate="%{y:.2f}%", textposition="inside")
    return fig


def financial_impact_delays_for_threshold_and_rentals_viz(
    dataset, range=range(0, 1000, 5)
):
    # Calculate avoidable losses for different thresholds
    results = []
    for threshold in range:
        dataset["avoidable_with_threshold"] = (
            dataset["time_delta_with_previous_rental_in_minutes"] < threshold
        ) & (dataset["is_potential_loss_due_to_delay"])
        avoidable_loss = dataset.loc[
            dataset["avoidable_with_threshold"], "estimated_loss"
        ].sum()
        results.append(
            {
                "threshold": threshold,
                "avoidable_loss": avoidable_loss,
            }
        )
    result_df = pd.DataFrame(results)
    fig = px.line(
        result_df,
        x="threshold",
        y="avoidable_loss",
        title="Impact financier des retards en fonction du seuil entre locations",
        labels={
            "threshold": "Seuil entre 2 locations",
            "avoidable_loss": "Pertes évitables ($)",
        },
    )
    fig.add_vline(
        x=delay, line_dash="dash", line_color="red", annotation_text="Délai sélectionné"
    )
    return fig


def plot_avoided_delays_vs_threshold_viz(data, range=range(0, 1000, 5)):
    avoided_delays_counts = []
    for threshold in range:
        threshold_data = data[
            data["time_delta_with_previous_rental_in_minutes"] < threshold
        ]

        avoided_delays = threshold_data[
            (threshold_data["is_potential_loss_due_to_delay"])
            & (
                threshold_data["delay_at_checkout_in_minutes"]
                > threshold_data["time_delta_with_previous_rental_in_minutes"]
            )
        ].shape[0]

        avoided_delays_counts.append(avoided_delays)

    results_df = pd.DataFrame(
        {
            "threshold": list(range),
            "avoided_delays": avoided_delays_counts,
        }
    )
    fig = px.line(
        results_df,
        x="threshold",
        y="avoided_delays",
        title="Évolution du nombre de retards évités en fonction du seuil",
        labels={
            "threshold": "Seuil entre 2 locations",
            "avoided_delays": "Nombre de retards évités",
        },
    )

    fig.add_vline(
        x=delay, line_dash="dash", line_color="red", annotation_text="Délai sélectionné"
    )

    return fig


def plot_delay_percentage_viz(dataset):
    filtered_data = dataset[
        dataset["time_delta_with_previous_rental_in_minutes"].notnull()
    ]
    # Créer une colonne pour déterminer si la location est en retard ou non
    filtered_data["is_late"] = filtered_data["delay_at_checkout_in_minutes"] > 0

    # Graphique 1 : Pourcentage de locations en retard
    late_counts = filtered_data["is_late"].value_counts()
    fig = px.pie(
        names=late_counts.index.map({True: "En retard", False: "À l'heure"}),
        values=late_counts.values,
        title="Pourcentage de locations en retard parmi celles avec une location précédente",
    )
    return fig


def plot_cancellation_due_to_delay_for_late_viz(dataset):
    filtered_data = dataset[
        dataset["is_cancel_due_to_delay_by_previous_rental"] == True
    ]
    state_counts = filtered_data["state"].value_counts()
    fig = px.pie(
        names=state_counts.index.map(
            {"canceled": "En retard et annulé", "ended": "En retard et non annulé"}
        ),
        values=state_counts.values,
        title="Taux d'annulation pour les locations ayant une précédente location en retard",
    )
    return fig


# Drop lines containing invalid values or outliers  [Xˉ−3σ,Xˉ+3σ][Xˉ−3σ,Xˉ+3σ]
def delete_ouliers(dataset, sigmas=3, columns=[]):
    """
    Delete outliers from Pandas dataset.

    1 sigma --> 68%
    2 sigmas --> 95%
    3 sigmas --> 99%


    Parameters:
    dataset (pd.DataFrame): Pandas dataset
    columns (list): list of the columns in dataset to check outliers. All by default.

    Returns:
    pd.DataFrame: clean dataset
    """
    masks = []
    if len(columns) < 1:
        columns = dataset.columns

    for col in columns:
        mean = dataset[col].mean()
        std = dataset[col].std()

        # 3 sigmas rules
        lower_bound = mean - sigmas * std
        upper_bound = mean + sigmas * std
        # print(f"For col {col}, lower is {lower_bound} and upper is {upper_bound}")

        # Create mask
        mask = (dataset[col] >= lower_bound) & (dataset[col] <= upper_bound)
        masks.append(mask)

    # Apply mask in all columns
    # example:
    # row1 = [0,1,1] -> [0]
    # row2 = [1,1,1] -> [1]
    final_mask = pd.concat(masks, axis=1).all(axis=1)
    filtered_df = dataset.loc[final_mask, :]
    return filtered_df


def get_correlation_matrix(corr_dataset):
    correlation_matrix = corr_dataset.corr()

    # Créer la figure
    fig = go.Figure(
        data=go.Heatmap(
            z=correlation_matrix,
            x=correlation_matrix.columns,
            y=correlation_matrix.columns,
            zmin=-1,  # Minimum de l'échelle de couleurs
            zmax=1,  # Maximum de l'échelle de couleurs
            text=correlation_matrix.round(2),  # Valeurs à afficher dans les cellules
            texttemplate="%{text:.2f}",  # Format des valeurs
            textfont={"size": 10},  # Taille de la police pour les valeurs
            hoverongaps=False,  # Désactiver le survol sur les cellules vides
            colorscale="RdBu",  # Échelle de couleurs rouge-bleu
            colorbar=dict(
                title="Correlation",  # Titre de la barre de couleurs
                titleside="right",
                thickness=15,
            ),
        )
    )
    # Mise à jour du layout
    fig.update_layout(
        title="Matrice de Corrélation Interactive",
        width=900,  # Largeur de la figure
        height=800,  # Hauteur de la figure
        xaxis=dict(
            tickangle=45,  # Rotation des labels de l'axe x
            side="bottom",
        ),
        yaxis=dict(
            autorange="reversed"  # Inverser l'axe y pour avoir la même disposition que seaborn
        ),
    )
    return fig


#############################################################################
#   Global variable
#############################################################################
# Price per minutes for location (calculate in notebook)
MEDIAN_DAY_PRICE = 119
MEDIAN_MINUTE_PRICE = 1.98
THRESHOLD_MINUTE_MAX = 400
MENU_EDA = "Exploration des données"
MENU_RESEARCH = "KPI"
MENU_BASICS_STATS = "Data"
MENU_OBSERVATIONS = "Observations"

#############################################################################
#   IHM
#############################################################################
if __name__ == "__main__":
    st.set_page_config(layout="wide")

    # Create a text element and let the reader know the data is loading.
    with st.spinner("Loading and 🧪 prepare data, delete outliers..."):
        rawdata = load_delay_analysis_data()
        dataprepared = prepare_data(data=rawdata)
        # data = delete_ouliers(
        #     dataset=dataprepared, sigmas=2, columns=["delay_at_checkout_in_minutes"]
        # )
        data = dataprepared

    with st.sidebar:
        st.header("🚀 Getaround")
        # stats_tab, answers_tab = st.tabs(["stats", "answers"])
        tab = st.sidebar.radio(
            "Menu", [MENU_BASICS_STATS, MENU_EDA, MENU_RESEARCH, MENU_OBSERVATIONS]
        )

    if tab == MENU_EDA:
        st.title("🧪 Exploration des données")

        st.markdown("---")

        st.write("### Exploration sur les données bruts.")

        st.markdown("---")

        # Display in 3 columns
        col1, col2, col3 = st.columns(3)
        with col1:
            fig = px.pie(
                rawdata,
                names="checkin_type",
                title="Répartition du type de récupération du véhicule",
            )
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            fig = px.pie(
                rawdata,
                names="state",
                title="Répartition des états des locations (finis ou annulées)",
            )
            st.plotly_chart(fig, use_container_width=True)
        with col3:
            fig = px.pie(
                dataprepared,
                names="is_potential_loss_due_to_delay",
                title="Répartition des pertes dues à un potentiel retard au checkout",
            )
            st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")

        fig = delay_distribution_viz(data=rawdata)
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")

        st.write("### Exploration des données nettoyées avec suppression des outliers.")

        st.markdown("---")

        fig = checkin_type_checkout_delay_viz(dataset=data)
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")

        fig = checkout_by_recovery_times_viz(dataset=data)
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")

        st.write("### Concentration sur les locations précédées d'une autre location.")

        st.markdown("---")

        col1, col2 = st.columns(2)
        with col1:
            fig = plot_delay_percentage_viz(data)
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            fig = plot_cancellation_due_to_delay_for_late_viz(data)
            st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")

    if tab == MENU_RESEARCH:
        st.title("🏗️ KPI")

        st.markdown("---")

        st.write("### Estimation des pertes.")
        # Slider to slect delay
        delay = st.slider(
            "**Choisir un délai en minutes**",
            min_value=0,
            max_value=1000,
            value=0,
            step=5,
        )

        # Display in 4 columns
        col1, col2, col3, col4 = st.columns(4)

        # Calculer les pertes potentielles basées sur le coût par minute de retard
        potential_loss = delay * MEDIAN_MINUTE_PRICE

        # Visualisation de l'impact des retards actuels dans les données
        data["estimated_loss"] = data["delay_at_checkout_in_minutes"].apply(
            lambda x: (x - delay) * MEDIAN_MINUTE_PRICE if (x - delay) > 0 else 0
        )

        total_loss_due_to_delays = data["estimated_loss"].sum()

        # Somme des retards évités
        threshold_data = data[
            data["time_delta_with_previous_rental_in_minutes"] < delay
        ]
        avoided_delays = threshold_data[
            (threshold_data["is_potential_loss_due_to_delay"])
            & (
                threshold_data["delay_at_checkout_in_minutes"]
                > threshold_data["time_delta_with_previous_rental_in_minutes"]
            )
        ].shape[0]

        with col1:
            st.markdown(
                f"""
                <div style="background-color: #6d9df5; padding: 10px; border-radius: 5px;">
                    <h3 style="color: white; text-align: center;">Prix médian par minute de retard</h3>
                    <p style="color: white; font-size: 20px; text-align: center;">{'${:,.2f}'.format(MEDIAN_MINUTE_PRICE)}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with col2:
            st.markdown(
                f"""
                <div style="background-color: #FCBA03; padding: 10px; border-radius: 5px;">
                    <h3 style="color: white; text-align: center;">Pertes potentielles par retard</h3>
                    <p style="color: white; font-size: 20px; text-align: center;">{'${:,.2f}'.format(potential_loss)}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with col3:
            st.markdown(
                f"""
                <div style="background-color: #FF4C4B; padding: 10px; border-radius: 5px;">
                    <h3 style="color: white; text-align: center;">Pertes totales dues aux retards</h3>
                    <p style="color: white; font-size: 20px; text-align: center;">{'${:,.2f}'.format(total_loss_due_to_delays)}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with col4:
            st.markdown(
                f"""
                <div style="background-color: #53f569; padding: 10px; border-radius: 5px;">
                    <h3 style="color: white; text-align: center;">Nombre de retards évités</h3>
                    <p style="color: white; font-size: 20px; text-align: center;">{avoided_delays}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown("---")

        with st.spinner("Loading..."):
            delay_values = list(range(0, 1000, 5))
            losses = [
                data["delay_at_checkout_in_minutes"]
                .apply(lambda x: (x - d) * MEDIAN_MINUTE_PRICE if (x - d) > 0 else 0)
                .sum()
                for d in delay_values
            ]

            fig = px.line(
                x=delay_values,
                y=losses,
                labels={
                    "x": "Délai minimum entre deux locations (minutes)",
                    "y": "Pertes estimées ($)",
                },
                title="Impact du seuil de délai sur la perte totale",
            )
            fig.add_vline(
                x=delay,
                line_dash="dash",
                line_color="red",
                annotation_text="Délai sélectionné",
            )
            st.plotly_chart(fig)

            st.markdown("---")

            fig = financial_impact_delays_for_threshold_and_rentals_viz(data)
            st.plotly_chart(fig)

            st.markdown("---")

            fig = plot_avoided_delays_vs_threshold_viz(data=data)
            st.plotly_chart(fig)

            st.markdown("---")

            st.write("### Perte estimée dans les données actuelles.")
            st.dataframe(
                data[
                    [
                        "rental_id",
                        "state",
                        "checkin_type",
                        "time_delta_with_previous_rental_in_minutes",
                        "delay_at_checkout_in_minutes",
                        "delay",
                        "estimated_loss",
                    ]
                ],
                height=600,
                use_container_width=True,
            )

    if tab == MENU_BASICS_STATS:
        st.title("📈 Data")

        st.markdown("---")

        st.markdown(
            """
            ### Observations sur le dataset

            **- Données en entrée :**
            
            J"avais commencé après analyse des données à enlever les outliers par rapport à la donnée `delay_at_checkout_in_minutes` mais cela m'a enlevé trop de données précieuses comme les annulation dues à un retard.
            J'ai donc décidé de garder l'ensemble du dataset.

            Par contre un enrichissement des données a été fait :

            - profit
            - delay ["0. Pas de retard", "1. Retard < 15 min", "2. 15 ≤ Retard < 60 min", "3. Retard ≥ 60 min"]
            - rental_count
            - critical_delay_for_next_rental_in_minutes
            - is_potential_loss_due_to_delay
            - is_cancel_due_to_delay_by_previous_rental
            """
        )

        st.markdown("---")

        st.markdown("**Données enrichies:**")

        st.write(dataprepared)

        st.markdown("---")

        st.markdown("**Statistiques Données bruts :**")

        stats = statistics.get_basics_statitics(data=data)
        for stat in stats.values():
            st.markdown(
                f"**{stat[0]}**",
            )
            st.write(stat[1])

        st.markdown("---")
        st.markdown("**Matrice de corrélation:**")

        corr_dataset = data[
            [
                "rental_id",
                "car_id",
                "checkin_type",
                "delay_at_checkout_in_minutes",
                "previous_ended_rental_id",
                "time_delta_with_previous_rental_in_minutes",
                "rental_count",
            ]
        ]
        corr_dataset["checkin_type"] = corr_dataset["checkin_type"].apply(
            lambda x: 1 if x == "connect" else 0
        )
        corr_dataset = corr_dataset.corr()
        fig = get_correlation_matrix(corr_dataset)
        st.plotly_chart(fig)

    if tab == MENU_OBSERVATIONS:
        st.title("💡 Observations")

        st.markdown("---")

        st.markdown(
            """
            ### Observations

            **- Proportion des retards :**

            - Environ 67% des locations avec le système Connect de Getaround (déverrouillage à distance) sont retournées à temps ou avec un léger retard (< 15 min).
            - Environ 51% des locations avec un retour en direct sont retournées à temps ou avec un léger retard (< 15 min).
            - Les retards significatifs (≥ 60 minutes) représentent environ 16% des locations via Connect et environ 30% pour celles en direct.
            - 15% des locations sont annulées.

            **- Impact financier des retards :**

            - Les retards importants, notamment ceux dépassant 60 minutes, entraînent des pertes financières plus élevées.
            - Le coût médian d'un retard est de **1,98 € par minute** ; ainsi, un retard de 60 minutes pourrait coûter près de **118,8 €**, corroboré par certaines valeurs de perte observées.

            **- Effet des retours précédents sur les locations suivantes :**

            - 43% des locations ayant eu une location avant, ne sont pas disponible due à un retard des précédent locataire.
            - 17% des précédentes locations sont annulées lorsqu'il y a un retard.

            **- Type de Check-in et état de location :**

            - Le type de check-in (mobile vs. connect) influence la durée du retard, et par conséquent les pertes financières, probablement en raison du temps nécessaire pour le retour du véhicule par le loueur et le locataire.

            **- Corrélations :**

            - Il existe une corrélation forte entre le type de checkin et le nombre de location d'un utilisateur. Les personnes disposant du dispositif connect getaround louent plus lors véhicule.

            ### Pistes d'amélioration

            **- Mise en place d'un délai minimum :**

            - Implémenter un délai minimum pour limiter les retards et les pertes financières. D'après la figure "Impact du seuil de retard sur la perte totale", un délai situé entre **300 et 400 minutes** pourrait être optimal.

            **- Remplacement automatique des véhicules :**

            - En cas de retard, envisager un remplacement du véhicule par un autre disponible pour réduire les pertes.
            - L’analyse des schémas de disponibilité des véhicules permettrait d’estimer les cas où un remplacement aurait pu éviter des retards et de proposer des améliorations dans la gestion de la flotte.

            **- Modèle de prédiction des retards :**

            - Utiliser les données existantes pour prédire les retards futurs et ajuster le délai minimum recommandé entre deux réservations.
            - En identifiant les facteurs les plus courants de retard (heure de la journée, jour de la semaine, type de client, etc.), un modèle prédictif pourrait suggérer des intervalles de temps adaptatifs entre deux locations.
            
            **- Check-in :**

            - Mettre en avant et insiter l'utilisation du check-in connect.
            
            """
        )
