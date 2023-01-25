from pydantic import BaseModel, Field
from typing import List
from datetime import date, datetime, time, timedelta
from enum import Enum
from typing_extensions import TypedDict


class ZoneImport(TypedDict):
    zone: int
    importFile: str


class Owner(BaseModel):
   owner_id: int | None = Field(default=None) # Used for associating a data dictionary to the owner.
   name: str
   states: List[str]
   website: str
   dataDictionary: str | None = Field(default=None)
   zones: List[ZoneImport] | None = Field(default=None)
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