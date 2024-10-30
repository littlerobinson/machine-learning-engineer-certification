import pandas as pd


def get_basics_statitics(data: pd.DataFrame):
    """
    Return the basics statistics from a dataframe

    Args:
    Data as pd.Dataframe

    Returns:
    Dictionnary :
    {
        "data_infos": data_infos,
        "stats": stats,
        "uniqs_by_features": uniqs_by_features,
        "missing_values": missing_values,
    }

    """
    ligns_infos = data.shape[0]
    columns_infos = data.shape[1]
    stats = data.describe(include="all")
    uniqs_by_features = data.nunique()
    missing_values = 100 * data.isnull().sum() / data.shape[0]

    response = {
        "ligns_infos": ("Nombre de lignes", ligns_infos),
        "columns_infos": ("Nombre de colonnes", columns_infos),
        "stats": ("Statitiques sur les données", stats),
        "uniqs_by_features": (
            "Nombre de valeurs uniques par feature",
            uniqs_by_features,
        ),
        "missing_values": ("Nombre de valeurs manquantes par feature ", missing_values),
    }

    return response
