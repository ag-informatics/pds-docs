from pydantic import BaseModel, Field
from typing import List, Any
from typing_extensions import TypedDict
from datetime import datetime

# Used for defining the data point entries for each plant in each zone.
class pointObject(TypedDict):
    field_id: int          # ID of the field this piece of data is associated with.
    value: Any             # Actual value of the data.
    version: int           # Version number.
    lastUpdated: datetime  # Time stamp of when the data was last updated.

# For defining a data dictionary object.
class PlantEntry(BaseModel):
    plant_id: int
    zone: int
    data: List[pointObject]
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

class Config:
    schema_extra = {
        # Add example response for schema
    }
    
def ResponseModel(data):
    return data

def ErrorResponseModel(error, code, msg):
    return {
        "error": error,
        "code": code,
        "message": msg,
    }