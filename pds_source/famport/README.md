# Using Famport to Bring In Data and Models
## About Famport
Famport, the (F)ast(A)PI (M)ongoDB Im(port)er, imports data into MongoDB and auto-generates FastAPI response models. It accepts both data dictionaries and data in CSV format and outputs a ``/models`` folder for FastAPI and connects directly to your MongoDB server to auto-populate a database with pre-defined JSON document collections.

The purpose of famport is to make defining Pydantic response schemas easy and fast! It is meant to be ideal for data dictionaries and models that have hundreds of different fields and a moderate level of complexity.

It is originally written for the Plant Data Service (PDS) and is created by Autumn Denny.

![famport explanation](https://user-images.githubusercontent.com/100234759/190932150-ebf3d663-f36e-4f4e-b8d1-877ec8a99914.png)

_Figure 1: famport mechanics._

## Installation
1. Install all requirements using ``pip install -r requirements.txt``
2. Put your data dictionaries and raw data files in ``/import_resources``
## Configuration
3. Configure using the config.yml file. Details explaining how to configure this file are commented in.
### MongoDB Server Authentication/Login

### Data Dictionary Requirements; Defining Collections
The data dictionary you use must follow some specific requirements. Here is a table explaining the requirements of a CSV data dictionary table:
| **Human-readable Name**  | **Machine-readable name** | **Description** | **Data Type** | **Enumeration Options** | **Collection** | **Requirement**|
| ------------- | ------------- | ------------- | ------------- | ------------- | ------------- | ------------- |
|**Accepted values**:  Any string. |**Accepted values**:  Any machine-readable string. Should not contain spaces or special characters. Optimally, use only numbers, characters, and underscores. |**Accepted values**:  Any string. |**Accepted values**: Must be one of the following to define data types: <ul><li>"string"</li><li>"float"</li><li>"date"</li><li>"integer"</li><li>"boolean"</li><li>"enum"</li></ul> |**Accepted values**: Any comma-separated strings. |**Accepted values**: Any string. |**Accepted values**: For a field to NOT be required, this can be left empty or have "false" or "no". _All other values are determined as stating that the field is required for the model._ |
| **Purpose**: This is the human-readable name of the field. It is mainly used for logging since the machine-readable name is used for the actual model construction. | **Purpose**: This is used to define the field in the model .py.| **Purpose**: This provides a description for the field. | **Purpose**: Used to define the data type for the field. Pydantic needs a data type for every field to keep consistency. | **Purpose**: If the data is an enumeration, the enumeration options should be added here. They must be strings, as of now. | **Purpose**: This tells famport what collection to use the field to define. All fields with the same "Collection" entry will be added into the same model .py. | **Purpose**: Allows for enforcing requirements on fields. |

The columns in your CSV MUST be in this order!


## How to run Famport
Simply go through the installation and configuration steps above. Then, run ```python3 famport.py``` in the home directory of famport.
You can also run famport by using ```python3 main.py --famport``` in the PDS home directory.

## Troubleshooting Famport
If you are noticing any issues, please view the log.txt that is generated when you run the script.