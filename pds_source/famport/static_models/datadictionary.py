from pydantic import BaseModel, Field
from typing import List
from typing_extensions import TypedDict, NotRequired
from datetime import datetime

# Used for defining the fields within a data dictionary.
class fieldObject(TypedDict, total = False):
    field_id: int                         # ID for the field. Used for tracking when fields are added, deleted, etc.       
    humanReadableName: str                # The "regular" version of the variable name. Example: "Species name"
    machineReadableName: str              # The machine-readable version of the variable name. Example: "species_name"
    dataType: str                         # The type of data to be used for instances of the field. Example: "string"
    description: str                      # The description of what the field is.
    required: bool                        # Whether or not the field is required for new entries.
    options: List[str]                    # If the data type is an enumeration or other choices type, these are the valid options.
    tags: List[str]                       # Additional functional tags. Example: "goals"
    version: int                          # Version of the field
    lastUpdated: datetime                 # Timestamp of when the field was editted

# For defining a data dictionary object.
class DataDictionary(BaseModel):
    owner_id : int                         # The PDS ID of the data owner associated with this data dictionary.
    fields : List[fieldObject]             # A list of field objects to define each field.
    version: int
    lastUpdated: datetime
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