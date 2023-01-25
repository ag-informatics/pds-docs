from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from pydantic import schema_json_of, BaseModel
# Get all the models!
from server import database as DB
import json


api = FastAPI()

def openAPISchema():
    openapi_schema = get_openapi(
        title = "The Plant Data Service",
        version = "MVP",
        description = "An open-access, open-source plant data API.",
        routes = api.routes,
    )
    openapi_schema["info"] = {
        "title": "The Plant Data Service",
        "version": "MVP",
        "description": "An open-access, open-source plant data API.",
        "contact": {
            "name": "Check out our GitHub:",
            "url": "https://github.com/ag-informatics/plant-data-service"
        },
    }
    api.openapi_schema = openapi_schema
    return api.openapi_schema


api.openapi = openAPISchema

@api.get("/", tags=["Root"])
async def read_root():
    return {"message": "This is the Plant Data Service."}

@api.get("/GetAllDataDictionaries")
def getAllDataDictionaries():
    return DB.retrieveDictionaries()

@api.get("/GetAllPlantDataByPlant")
def getPlantData(plant_id: int):
    return DB.retrieveAllDataOfPlant(plant_id)

@api.get("/GetCoverCropsFromPlant")
def getCoverCropDataByPlant(plant_id: int):
    return DB.retrieveCoverCropsFromPlant(plant_id)

# Here's for geographic functionality.
@api.get("/GetCoverCropsFromPlantFromCounty")
def getCoverCropDataByPlantByCounty(county: str, state: str, plant_id: int):
    pass