from fastapi import FastAPI

tags_metadata = [
    {
        "name": "data",
        "description": "Show data",
    },
    {"name": "machine-learning", "description": "Prediction Endpoint."},
]

app = FastAPI(
    title="🪐 Data Sciences API",
    description="API for data sciences dataset",
    version="0.1",
    contact={
        "name": "Alexandre",
        "url": "https://github.com/littlerobinson",
    },
    openapi_tags=tags_metadata,
)


@app.get("/")
async def root():
    return {"message": "Hello Data Science Application!"}
