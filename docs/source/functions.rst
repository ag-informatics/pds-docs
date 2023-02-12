API Functions
==============================================

Retrieving Data Dictionaries
*****************
Retrieves all data dictionaries used within the PDS and their respective data owners.
**Arguments**: *None*
**Response**: ::

{
  "dictionaries": [
    {
      "owner_id": 0,
      "fields": [
        {
          "field_id": #,
          "humanReadableName": "",
          "machineReadableName": "",
          "dataType": "",
          "description": "",
          "required": false,
          "tags": [
            ""
          ],
          "version": 0,
          "lastUpdated": "2023-02-03T14:34:49.984000"
        },
        {
          "field_id": #,
          ...
        }
      ]
    }
   ]
}

Retrieving All Data By Plant
*****************
Retrieves all data associated with a plant.
**Arguments**: Plant ID (int)
**Response**: ::

{
  "plants": [
    {
      "plant_id": #,
      "zone": #,
      "data": [
        ...
      ]
    }
  ]
}

Retrieving Cover Crop Data By Plant
*****************
Retrieves all cover cropping-related data associated with a plant, including cover crop goals. 
**Arguments**: Plant ID (int)
**Response**: ::

{
  "plants": [
    {
      "plant_id": #,
      "zone": #,
      "data": [
        ...
      ]
     {
  ]
}

