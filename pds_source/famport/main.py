import argparse
import os
import sys
import yaml
from yaml.loader import SafeLoader
import utils_config as ConfigUtils
import data_importer

# Importing the modules I wrote as part of famport.
import csv_parser as CSVParser
import model_constructor as models
#import data_importer as importer

print("famport: The FastAPI MongoDB Importer")
print("-------------------------------------------------")
print("Ensure your data dictionary and data files are in the /import_resources directory.")
print(ConfigUtils.config)
# Adding arguments for telling Famport which tool you want to use.
parser = argparse.ArgumentParser(description = 'Famport')
parser.add_argument("--createModels", help = "Creates dynamic models for each grouping defined in the data dictionary for a data owner. These models are code expressions of each category defined in the data dictionaries in the config.yml and they are used by Pydantic for object relational mapping.", action = "store_true")
parser.add_argument("--importAllDataAndDictionaries", help = "Imports all data and dictionaries defined in the config.yml. All import CSVs must be stored in /import_resources.", action = "store_true")
parser.add_argument("--importDataDictionaries", help = "Updates the data dictionaries in the MongoDB database if they already exist, or imports dictionaries into the database if it has not been done before.", action = "store_true")
arguments = parser.parse_args()

if arguments.createModels == True:
    print("You are regenerating new models. This will overwrite anything in the famport_registered_schemas database collection. It will also rewrite any existing model schemas in /dynamic_models.")
    confirmation = input("Do you still wish to proceed? Y/N: ")
    if confirmation.lower() == 'y':
    # Goes through owners in config.yml and creates models from each data dictionary defined.
        for owner in ConfigUtils.config.dataOwners :
            if owner.dataDictionary:
                # We have to check to make sure that the data dictionary is in import_resources and is a csv file.
                dataDictFile = "import_resources/" + owner.dataDictionary
                dataDictFileType = os.path.splitext(dataDictFile)[1]
                if dataDictFileType == ".csv": 
                    # Parses the data dictionary and then passes this along to the model constructor.
                    dataDict = CSVParser.parseCSV(dataDictFile)
                    models.constructModels(dataDict, owner.name)
                    # The model constructor also registers the model schema to famport_registered_schemas.
        print("Model creation completed! Check log.txt to see if anything was omitted.")
    else:
        print("Aborting!")
if arguments.importAllDataAndDictionaries == True:
    print("You are importing all data and dictionaries defined in the config.yml. This may overwrite some existing data.")
    confirmation = input("Do you still wish to proceed? Y/N: ")
    if confirmation.lower() == 'y':
        data_importer.importDictionaries()
        data_importer.importData()
    else:
        print('Aborting!')
if arguments.importDataDictionaries == True:
    data_importer.importDictionaries()

