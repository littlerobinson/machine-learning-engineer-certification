# 🚗 Getaround

## 1. 📝 Description

Ce projet à 2 Objectifs :

- Un dashboard permettant de donner des pistes d'amélioration pour contrer les nombreux retards que subissent les loueurs de voitures.
- La prédiction de prix pour les voitures via une API utilisant un modèle de machine learning déployé avec MLflow. L'API permet de prédire le prix d'une voiture en fonction de diverses caractéristiques telles que le kilométrage, la puissance du moteur, les équipements, etc.

## 2. 🌍 Contexte

Getaround est le "Airbnb des voitures". Vous pouvez louer des voitures à n'importe qui pour quelques heures ou quelques jours ! 🚙 Fondée en 2009, cette entreprise a connu une croissance rapide et, en 2019, compte plus de 5 millions d'utilisateurs et environ 20 000 voitures disponibles dans le monde.

Sur Getaround, les conducteurs réservent des voitures pour une durée déterminée, allant d'une heure à plusieurs jours. Ils sont censés rendre la voiture à temps, mais des retards de restitution peuvent créer de fortes frictions pour le client suivant 🚦.

### Objectifs 🎯

Ce projet à 2 Objectifs :

- La prédiction de prix pour les voitures via une API utilisant un modèle de machine learning déployé avec MLflow. L'API permet de prédire le prix d'une voiture en fonction de diverses caractéristiques telles que le kilométrage, la puissance du moteur, les équipements, etc.
- Un dashboard permettant de donner des pistes d'amélioration pour contrer les nombreux retards que subissent les loueurs de voitures.
  Pour limiter ces problèmes, nous avons décidé de mettre en place un délai minimum entre deux locations. Une voiture ne sera pas affichée si l'horaire de la nouvelle réservation est trop proche d'une location existante.
  Cela résout le problème des retards, mais peut aussi réduire les revenus de Getaround et des propriétaires : nous devons donc trouver le bon compromis ⚖️.

## 3. 🔧 Prérequis

- Docker 🐳
- Docker Compose

## 4. 🚀 Installation

1. Clonez le dépôt :

   ```sh
   git clone https://github.com/littlerobinson/ai-architect-certification/tree/main/getaround
   cd getaround
   ```

2. Construisez et lancez les services avec Docker Compose :

   ```sh
   docker-compose up --build
   ```

## 🧑‍🏫 Entraînement

Ce script lance des entraînements et génère des modèles historisés sur MLFlow.

Lancer un jeu d'entraînement :

```bash
cd training
python app.py
```

Vous pouvez visualiser l'historique des entraînements ici : [https://getaround-mlflow-jedha.luciole.dev](https://getaround-mlflow-jedha.luciole.dev)

## 5. 🌐 API

Une API est disponible pour demander une prédiction du tarif journalier d'une voiture 🚘.

Accès à l'API : [https://getaround-api-jedha.luciole.dev](https://getaround-api-jedha.luciole.dev)

Documentation de l'API : [https://getaround-api-jedha.luciole.dev/docs](https://getaround-api-jedha.luciole.dev/docs)

### Endpoint de prédiction

L'API expose un endpoint `/predict` pour effectuer des prédictions de prix.

#### Exemple de requête

```sh
curl -X POST "https://getaround-api-jedha.luciole.dev/getaround/predict" -H "Content-Type: application/json" -d '{
  "mileage": 10000,
  "engine_power": 120,
  "private_parking_available": true,
  "has_gps": true,
  "has_air_conditioning": true,
  "automatic_car": true,
  "has_getaround_connect": true,
  "has_speed_regulator": true,
  "winter_tires": true,
  "model_key": "peugeot",
  "fuel": "diesel",
  "paint_color": "red",
  "car_type": "sedan"
}'
```

#### Exemple de réponse

```json
{
  "prediction": 123.2
}
```

## 📁 Structure du projet

- `api/` : Contient le code de l'API et le Dockerfile.
- `dashboard/` : Contient le code du tableau de bord et le Dockerfile.
- `mlflow/` : Dockerfile pour MLFlow.
- `app.py` : Contient le script d'entrainement.

```bash
.
├── api
│   └── src
│       ├── data
│       ├── handlers
│       ├── models
│       └── routers
├── dashboard
│   └── src
│       ├── data
│       ├── functions
├── data
├── mlflow
├── mlruns
│   ├── 0
│   ├── 296131423263316523
│   │   ├── 00c7d105ff3f4cb8a1cc140de751b5af
│   │   │   ├── artifacts
│   │   │   │   └── getaround-price-prediction
│   │   │   ├── metrics
│   │   │   ├── params
│   │   │   └── tags
│   └── models
│       ├── Gradient Boosting
│       │   └── version-1
│       ├── Lasso
│       │   └── version-1
│       ├── Linear Regression
│       │   ├── version-1
│       │   ├── version-2
│       │   └── version-3
│       ├── Random Forest
│       │   └── version-1
│       ├── Ridge
│       │   ├── version-1
│       │   └── version-2
│       └── XGBoost
│           └── version-1
└── notebooks
└── app.py
└── docker-compose.yml
└── MLproject
└── README.md
└── run.sh
└── secrets.sh
```

## 6. 📊 Dashboard

Un tableau de bord est accessible ici : [https://getaround-dashboard-jedha.luciole.dev](https://getaround-dashboard-jedha.luciole.dev)

### 🔍 Questions clés

Le projet vise à répondre aux questions suivantes :

- ⏱️ Seuil : quelle doit être la durée minimale du délai ?
- 🌍 Portée : devons-nous activer cette fonctionnalité pour toutes les voitures, ou uniquement pour celles connectées ?
- 📉 Quel pourcentage des revenus des propriétaires pourrait être impacté ?
- 🔄 Combien de locations seraient affectées en fonction du seuil et de la portée choisis ?
- 🕰️ À quelle fréquence les conducteurs sont-ils en retard pour la restitution, et quel impact cela a-t-il ?
- ✅ Combien de cas problématiques cela pourrait-il résoudre ?
