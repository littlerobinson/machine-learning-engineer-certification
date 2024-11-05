from fastapi import APIRouter, HTTPException, Response

import src.handlers.getaround_handler as gh
from src.models.getaround_model import GetaroundModel

import json


router = APIRouter(
    prefix="/getaround",
    # tags=["getaround"],
    responses={404: {"description": "Not found"}},
)


@router.get("/")
async def root():
    """
    Root endpoint to check the status of the getaround API.

    Returns:
        dict: A message indicating the API is working.
    """
    return {"message": "Hello Geataround"}


@router.get("/sample", tags=["data"])
async def sample(count: int = 10):
    """
    Endpoint to get a sample of rows from the Geataround data.

    Args:
        count (int, optional): The number of rows to sample. Defaults to 10.

    Returns:
        Response: A JSON response containing the sampled rows.
    """
    response = await gh.sample(count)
    return Response(response.to_json(orient="records"), media_type="application/json")


@router.get("/unique-values", tags=["data"])
async def unique_values(column: str):
    """
    Endpoint to get unique values from a specified column in the Geataround data.

    Args:
        column (str): The name of the column to retrieve unique values from.

    Returns:
        Response: A JSON response containing the unique values from the specified column.

    Raises:
        HTTPException: If the column does not exist.
    """
    response = await gh.unique_values(column)
    if response is False:
        raise HTTPException(status_code=404, detail="Item not found")
    return Response(response.to_json(orient="records"), media_type="application/json")


@router.post("/predict", tags=["machine-learning"])
async def predict(data: GetaroundModel):
    response = await gh.predict(data)
    return Response(content=json.dumps(response), media_type="application/json")
