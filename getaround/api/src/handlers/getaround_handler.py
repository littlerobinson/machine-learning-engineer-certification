import os
import mlflow
import pandas as pd

from src.models.getaround_model import GetaroundModel


async def sample(count: int):
    """
    Asynchronous function to sample a specified number of rows from the Excel file.

    Args:
        count (int): The number of rows to sample.

    Returns:
        pd.DataFrame: A DataFrame containing the sampled rows.
    """
    df = pd.read_csv("/app/src/data/get_around_pricing_project.csv")
    sample = df.sample(count)
    return sample


async def unique_values(column: str):
    """
    Asynchronous function to get unique values from a specified column in the Excel file.

    Args:
        column (str): The name of the column to retrieve unique values from.

    Returns:
        pd.Series: A Series containing the unique values from the specified column, or False if the column does not exist.
    """
    df = pd.read_csv("/app/src/data/get_around_pricing_project.csv")
    # Check if column exist
    if column not in df:
        return False

    return pd.Series(df[column].unique())


async def predict(input_data: GetaroundModel):
    """
    Prediction.

    Args:
        {
            mileage: double
            engine_power: double
            private_parking_available: bool
            has_gps: bool
            has_air_conditioning: bool
            automatic_car: bool
            has_getaround_connect: bool
            has_speed_regulator: bool
            winter_tires: bool
            model_key: category
            fuel: category
            paint_color: category
            car_type: category
        }
    Example:
        {
            "mileage": 120000,
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
            "paint_color": "white",
            "car_type": "suv"
        }
    """
    rawdf = pd.read_csv("/app/src/data/get_around_pricing_project.csv")

    # Transform data
    df = pd.DataFrame(dict(input_data), index=[0])

    df["mileage"] = df["mileage"].astype("int32")
    df["engine_power"] = df["engine_power"].astype("int32")
    df["private_parking_available"] = df["private_parking_available"].astype("bool")
    df["has_gps"] = df["has_gps"].astype("bool")
    df["has_air_conditioning"] = df["has_air_conditioning"].astype("bool")
    df["automatic_car"] = df["automatic_car"].astype("bool")
    df["has_getaround_connect"] = df["has_getaround_connect"].astype("bool")
    df["has_speed_regulator"] = df["has_speed_regulator"].astype("bool")
    df["winter_tires"] = df["winter_tires"].astype("bool")

    df["model_key"] = df["model_key"].astype("str").str.lower()
    df["fuel"] = df["fuel"].astype("str").str.lower()
    df["paint_color"] = df["paint_color"].astype("str").str.lower()
    df["car_type"] = df["car_type"].astype("str").str.lower()

    # If model key not exist replace with "other" value
    model_key_values = pd.unique(rawdf["model_key"].str.lower())
    if df["model_key"][0] not in model_key_values:
        df["model_key"][0] = "other"

    MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI")
    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)

    # Log model from mlflow
    MLFLOW_LOGGED_MODEL = os.getenv("MLFLOW_LOGGED_MODEL")
    logged_model = MLFLOW_LOGGED_MODEL

    # If you want to load model persisted locally
    # loaded_model = joblib.load('doctor-cancellation-detector/model.joblib')

    # Load model as a PyFuncModel.
    loaded_model = mlflow.pyfunc.load_model(logged_model)

    prediction = loaded_model.predict(df)

    # Format response
    response = {"prediction": prediction.tolist()[0]}
    return response
