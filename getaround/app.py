import os

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
import xgboost as xgb
from dotenv import load_dotenv
from sklearn.compose import ColumnTransformer
from sklearn.discriminant_analysis import StandardScaler
from sklearn.ensemble import (
    GradientBoostingRegressor,
    RandomForestRegressor,
)
from sklearn.linear_model import Lasso, LinearRegression, Ridge
from sklearn.metrics import root_mean_squared_error, r2_score
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

import mlflow
from mlflow.models.signature import infer_signature


class LowercaseTransformer(BaseEstimator, TransformerMixin):
    def fit(self, X, y=None):
        return self

    def transform(self, X, y=None):
        return X.apply(lambda x: x.str.lower() if x.dtype == "object" else x)


if __name__ == "__main__":
    print("getaround price prediction")

    # Load the environment variables
    load_dotenv()

    # Init for MLflow
    MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI")
    print(f"Call MLflow URI: {MLFLOW_TRACKING_URI}")
    EXPERIMENT_NAME = "jedha-getaround-price-prediction"

    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
    mlflow.set_experiment(EXPERIMENT_NAME)

    # Get our experiment info
    experiment = mlflow.get_experiment_by_name(EXPERIMENT_NAME)

    # Load data
    dataset_path = "./data/get_around_pricing_project.csv"
    rawdata = pd.read_csv(dataset_path)

    # Prepare data
    dataset = rawdata.drop(columns=["Unnamed: 0"])
    car_type_counts = dataset["car_type"].value_counts()
    car_type_percentages = (car_type_counts / len(dataset) * 100).round(2)
    model_car_counts = dataset["model_key"].value_counts()
    model_car_percentages = (model_car_counts / len(dataset) * 100).round(2)
    # Regroupement des données model_key et car_type ayant peu de données
    car_type_counts = dataset["car_type"].value_counts(normalize=True).mul(100).round(2)
    car_type_mask = car_type_counts > 5.0
    dataset["car_type"] = dataset["car_type"].apply(
        lambda x: x if car_type_mask[x] else "other"
    )
    model_key_counts = (
        dataset["model_key"].value_counts(normalize=True).mul(100).round(2)
    )
    model_key_mask = model_key_counts > 1.0
    dataset["model_key"] = dataset["model_key"].apply(
        lambda x: x if model_key_mask[x] else "other"
    )

    # Create the model
    numeric_features = [
        "mileage",
        "engine_power",
        "private_parking_available",
        "has_gps",
        "has_air_conditioning",
        "automatic_car",
        "has_getaround_connect",
        "has_speed_regulator",
        "winter_tires",
    ]
    categorical_features = ["model_key", "fuel", "paint_color", "car_type"]

    # Preprocessing
    # Transform also cat var to lowercase
    preprocessor = ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), numeric_features),
            (
                "cat",
                Pipeline(
                    steps=[
                        ("lowercase", LowercaseTransformer()),
                        ("onehot", OneHotEncoder()),
                    ]
                ),
                categorical_features,
            ),
        ]
    )

    models = {
        "Linear Regression": LinearRegression(),
        "Ridge": Ridge(alpha=1.5),
        "Lasso": Lasso(alpha=0.6),
        "Random Forest": RandomForestRegressor(n_estimators=100, random_state=42),
        "Gradient Boosting": GradientBoostingRegressor(
            n_estimators=100, random_state=42
        ),
        "XGBoost": xgb.XGBRegressor(n_estimators=100, random_state=42),
    }

    # Enable mlflow autolog
    mlflow.sklearn.autolog(disable=True)
    # mlflow.autolog(disable=True)

    def evaluate_regression_models(
        X, y, scoring="r2", test_size=0.2, random_state=42, n_jobs=1
    ):
        # Split des données
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state
        )

        for model_name, model in models.items():
            # Création du pipeline
            pipeline = Pipeline([("preprocessor", preprocessor), ("regressor", model)])

            # Entraînement
            pipeline.fit(X_train, y_train)

            # Prédictions
            y_pred = pipeline.predict(X_test)

            # Calcul des métriques
            rmse_value = root_mean_squared_error(y_test, y_pred)
            r2_value = r2_score(y_test, y_pred)
            mae_value = np.mean(np.abs(y_test - y_pred))

            # Cross-validation
            cv_scores = cross_val_score(
                pipeline, X, y, cv=10, scoring=scoring, n_jobs=n_jobs
            )

            # Prédiction sur un échantillon de données
            sample_data = (
                X_test.iloc[0].to_frame().T
            )  # Prendre la première ligne de X_test comme échantillon
            sample_prediction = pipeline.predict(sample_data)

            # Log experiment to MLFlow
            with mlflow.start_run(experiment_id=experiment.experiment_id) as run:
                mlflow.log_param("dataset_path", dataset_path)

                # mlflow.log_input(mlflow.data.dataset.Dataset(dataset_path))
                mlflow.log_param("Datasets used", dataset_path)

                # Log des résultats
                print(f"\n{model}:")
                # Log Params
                mlflow.log_param("random_state", random_state)
                mlflow.log_param("n_jobs", n_jobs)
                mlflow.log_param("test_size", test_size)
                # Log Metrics
                mlflow.log_metric("rmse", rmse_value)
                mlflow.log_metric("mae", mae_value)
                mlflow.log_metric("r2_score", r2_value)
                mlflow.log_metric("cv_mean", cv_scores.mean())
                mlflow.log_metric("cv_std", cv_scores.std())

                # Log the sklearn model and register as version
                mlflow.sklearn.log_model(
                    sk_model=pipeline,  # Note: model should be the trained instance
                    artifact_path=EXPERIMENT_NAME,
                    registered_model_name=model_name,
                    signature=infer_signature(
                        X[:1],
                        sample_prediction.tolist(),
                    ),
                )


# Preprocess data
# Separate features and target
X = dataset[numeric_features + categorical_features]
y = dataset["rental_price_per_day"]

# Évaluation des modèles
test_size = 0.2
random_state = 42
n_jobs = -1
evaluate_regression_models(
    X, y, test_size=test_size, random_state=random_state, n_jobs=n_jobs
)


print("...Done!")
