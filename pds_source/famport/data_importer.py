from static_models import datadictionary
from utils_config import config
import csv_parser as CSVParser
import os 
import logger
import json
import utils_database as DatabaseUtils
from datetime import datetime
from static_models.entry import PlantEntry
import re

def importDictionaries():
    # Loops through all owners defined in the config and addresses those with valid data dictionaries.
    for owner in config.dataOwners:

        if owner.dataDictionary:
            print("Data dictionary for " + owner.name + " found. Importing now ...")
            # Opens up and parses the data dictionary. See the Famport README for how data dictionaries are read.
            dataDictFile = "import_resources/" + owner.dataDictionary
            dataDictFileType = os.path.splitext(dataDictFile)[1]

            if dataDictFileType == ".csv":
                dataDict = CSVParser.parseCSV(dataDictFile)

            # Logs if the data dictionary entered in the configuration is not a CSV.
            else:
                logger.record("The data dictionary for " + owner.name + " is not a CSV. It has been skipped.")
                continue

            dictionaryInstance = {}                           # Creates a dictionary to be parsed into a DataDictionary object.
            dictionaryInstance['owner_id'] = owner.owner_id   # Maps an owner ID to the dictionary.

            # Now we start creating fields based on the data dictionary given.
            fields = []                                       # List of field dictionaries.
            index = 1
            for field in dataDict:
                fieldDict = {}
                # Gets the human-readable name of the field. Skips if there is none defined.
                if field[0].strip() != '':
                    fieldDict['humanReadableName'] = field[0]
                else:
                    logger.record("Field #" + str(index) + " in the " + owner.name + " data dictionary does not have a valid human-readable name and has been skipped on data dictionary import.") 
                    continue
                # Gets the machine-readable name of the field. Skips if there is none defined.
                if field[1].strip() != '':
                    fieldDict['machineReadableName'] = field[1]
                else: 
                    logger.record("Field #" + str(index) + " in the " + owner.name + " data dictionary does not have a valid machine-readable name and has been skipped on data dictionary import.")
                    continue
                # Gets the description of the field.
                fieldDict['description'] = field[2]
                # Gets the enum choices, if there are any.
                if field[4].strip() != '':
                    fieldDict['options'] = field[4].split(",")   # Assumes the enum choices are comma-separated.
                # Skips the field if there is an 'enum' type with no options.
                if field[4].strip() == '' and field[3].lower().strip() == 'enum':
                        logger.record("Field #" + str(index) + " in the " + owner.name + " data dictionary is listed as an enum but has no valid enumeration options and has been skipped on data dictionary import.")
                        continue
                # Gets the data type of the field. Skips if there is no valid data type defined.
                if field[3].lower().strip() != "string" and field[3].lower().strip() != "integer" and field[3].lower().strip() != "boolean" and field[3].lower().strip() != "float" and field[3].lower().strip() != "date" and field[3].lower().strip() != "enum":
                    logger.record("Field #" + str(index) + " in the " + owner.name + " data dictionary does not have a valid data type and has been skipped on data dictionary import.")
                    continue
                else:
                    fieldDict['dataType'] = field[3].lower().strip()
                # Gets the categorical assignment of this piece of information.
                if field[5].strip() == '':
                    logger.record("Field #" + str(index) + " in the " + owner.name + " data dictionary does not have a valid categorical assignment or tags and has been skipped on data dictionary import.")
                else:
                    # Multi-grouping support, right here!
                    if ',' in field[5]:
                        tagList = field[5].split(',')
                    else:
                        tagList = []
                        tagList.append(field[5])
                    fieldDict['tags'] = tagList
                # Get whether or not the field is required.
                if field[6].lower().strip() == '' or field[6].lower().strip() == 'false' or field[6].lower().strip() == 'no':
                    fieldDict['required'] = False
                else:
                    fieldDict['required'] = True
                fields.append(fieldDict)
                # Used for tracking changes in the data dictionary on the per-field level.
                fieldDict['field_id'] = index
                fieldDict['version'] = 0
                fieldDict['lastUpdated'] = datetime.now()
                index += 1
            # Assigns the fields to the proper attribute of the dictionary object
            dictionaryInstance['fields'] = fields

            # We timestamp our version.
            dictionaryInstance['version'] = 0
            dictionaryInstance['lastUpdated'] = datetime.now()

            # We now have a fully constructed dictionary object validated with Pydantic:
            data = datadictionary.DataDictionary.parse_obj(dictionaryInstance)
            # Run MongoDB operations to update or add datadictionary.
            DatabaseUtils.registerDicts(data.dict())
            

def importData():
    # Loops through all owners defined in the config and addresses those with valid data inputs.
    for owner in config.dataOwners:
        # Loops through the zones.
        if owner.zones:
            for zone in owner.zones:
                # Gets the zone number
                zoneNumber =str(zone['zone'])
                # Parses the CSV and determines how many entries are in it.
                zoneFile = 'import_resources/' + zone['importFile']
                zoneData = CSVParser.csvRead(zoneFile)
                numberOfEntries = CSVParser.getEntries(zoneFile)
                print('Found data for ' + owner.name + ' for zone ' + zoneNumber + ' ...')
                # Pulls up the data dictionary associated with this particular data owner.
                matchedDictionary = DatabaseUtils.getDataDictionary(owner.owner_id)
                dictFields = matchedDictionary['fields']
                # We also need the variable names in the raw data file.
                dataFields = zoneData.keys()
                for field in dictFields:
                    if field['humanReadableName'] not in dataFields:
                        logger.record('Note: Your raw data for ' + owner.name + 'and zone ' + zoneNumber + ' does not include a variable: ' + field['humanReadableName'])
                # We loop through each of the pieces of data for a plant.
                organizedPlantDataCollection = []
                for i in range(numberOfEntries):
                    plantData = []
                    for field in dataFields:
                        dataPoint = {}
                        for dictField in dictFields:
                            if field == dictField['humanReadableName']:
                                dataPoint['field_id'] = dictField['field_id']
                                dataPoint['name'] = dictField['humanReadableName']                          
                                dataPoint['value'] = zoneData[field][i]
                                plantData.append(dataPoint)
                    organizedPlantDataCollection.append(plantData)
                # We create a list of plants for registration into the database. This is used for assigning plant_ids for plants to be quickly recognized across zones and data owners.
                for item in organizedPlantDataCollection:
                    # Plants are recognized as "new" if they have a different cover crop name, scientific name, and synonyms listing than the plants in the database
                    for field in item:
                        if field['name'] == "Cover Crop Name":
                            name = field['value']
                        if field['name'] == 'Scientific Name':
                            scientificName = field['value']
                        if field['name'] == 'Synonyms':
                            synonyms = field['value']
                    DatabaseUtils.registerPlant(name, scientificName, synonyms)

                    # This may all get moved into another function at some point in some stage of refactoring...
                    # This next bit is all validation of the data value against the data dictionary.
                    # If something doesn't match up, we log it into log.txt
                plants = []
                for item in organizedPlantDataCollection:   # For plant in the whole collection.
                    plant = {}
                    plantFields = []
                    for field in item:                      # For each field in the plant
                        # These next 'if' statements are for identifying unique plants.
                        # These are included in the plant_library collection in MongoDB
                        if field['name'] == "Cover Crop Name":
                            name = field['value']
                        if field['name'] == 'Scientific Name':
                            scientificName = field['value']
                        if field['name'] == 'Synonyms':
                            synonyms = field['value']
                        for dictField in dictFields:        # For each field in the data dictionary (for matching to plant field)
                            if dictField['field_id'] == field['field_id']:
                                fieldInfo = {}
                                dictType = dictField['dataType']
                                if dictType == 'enum' and field['value'] != '':
                                    # Handles integer enum choices. Turns them into indexes that point to a specific value in the data dictionary 'options' for that field.
                                    try:
                                        int(value)   # Just confirms that the value can be turned into an integer.
                                        # For handling lists of integer choices
                                        if ',' in field['value']:
                                            value = []
                                            selection = field['value'].split(',')
                                            for choice in selection:
                                                choice = int(item) - 1
                                                if choice <= len(dictField['options']):
                                                    value.append(choice)
                                                else: 
                                                    logger.record('Enum option for plant ' + str(item['plant_id']) + ' in zone ' + zoneNumber + ' for owner ' + owner.name + ' out of range.')
                                                    value = None
                                                    continue
                                        # For handling single integer choices.
                                        else: 
                                                choice = int(field['value'])
                                                value = []
                                                if choice <= len(dictField['options']):
                                                    value.append(choice - 1)
                                                else: 
                                                    logger.record('Enum option for plant ' + str(item['plant_id']) + ' in zone ' + zoneNumber + ' for owner ' + owner.name + ' out of range.')
                                                    value = None
                                                    continue
                                        fieldInfo['value'] = value
                                        fieldInfo['version'] = 0
                                        fieldInfo['lastUpdated'] = datetime.now()
                                        fieldInfo['field_id'] = dictField['field_id']
                                        plantFields.append(fieldInfo)
                                    # This handles string enum values. Pretty much in the same fashion that integer choices are handled.
                                    except:
                                        reformattedOptions = []
                                        for option in dictField['options']:
                                            reformattedOptions.append(option.lower().strip())
                                        if ',' in field['value']:
                                            value = []
                                            selection = field['value'].split(',')
                                            for choice in selection:
                                                index = 0
                                                for option in reformattedOptions:
                                                    if option == choice.lower().strip():
                                                        value.append(index)
                                                    index += 1
                                        else:
                                            value = []
                                            choice = field['value'].lower().strip()
                                            index = 0
                                            for option in reformattedOptions:
                                                if option == choice:
                                                    value.append(index)
                                                index += 1
                                        # This part that uses regex is useful for enum choices like "Poor" or "Good"
                                        # Where the data dictionary options look like "Poor-Does not handle drainage" or "Good-Handles drainage"
                                        # Basically, it tries to match the data values with something like it in the data dictionary.
                                        # It gets mad and logs to log.txt if it can't find an appropriate match.
                                        if value == []:
                                            if ',' in field['value']:
                                                for choice in field['values']:
                                                    choice = choice.lower().strip()
                                                    index = 0
                                                    for option in reformattedOptions:
                                                        reOption = re.findall("[\dA-Za-z]*", option.lower().strip())[0]
                                                        if reOption == choice:
                                                            value.append(index)
                                                        index += 1
                                            else:
                                                choice = field['value'].lower().strip()
                                                value = []
                                                index = 0
                                                for option in reformattedOptions:
                                                    reOption = re.findall("[\dA-Za-z]*", option.lower().strip())[0]
                                                    if reOption == choice:
                                                        value.append(index)
                                                    index += 1
                                        if value == [] or value is None:
                                            logger.record("There was a problem validating an enum for a plant's data for zone " + zoneNumber + " and owner " + owner.name + '. Field ID = ' + str(field['field_id']) + ', Raw data option = ' + str(field['value']))
                                            continue
                                        fieldInfo['value'] = value
                                        fieldInfo['version'] = 0
                                        fieldInfo['lastUpdated'] = datetime.now()
                                        fieldInfo['field_id'] = dictField['field_id']
                                        plantFields.append(fieldInfo)
                                if dictType == 'string' and field['value'] != '':
                                    try:
                                        value = str(field['value'])
                                        fieldInfo['value'] = value
                                        fieldInfo['version'] = 0
                                        fieldInfo['lastUpdated'] = datetime.now()
                                        fieldInfo['field_id'] = dictField['field_id']
                                        plantFields.append(fieldInfo)
                                    except:
                                        logger.record("There was a problem validating a string for a plant's data for zone " + zoneNumber + " and owner " + owner.name)
                                        continue
                                if dictType == 'float' and field['value'] != '':
                                    try:
                                        value = float(field['value'])
                                        fieldInfo['version'] = 0
                                        fieldInfo['lastUpdated'] = datetime.now()
                                        fieldInfo['field_id'] = dictField['field_id']
                                        fieldInfo['value'] = value
                                        plantFields.append(fieldInfo)
                                    except:
                                        logger.record("There was a problem validating a float for a plant's data for zone " + zoneNumber + " and owner " + owner.name)
                                        continue
                                if dictType == 'integer' and field['value'] != '':
                                    try:
                                        value = int(field['value'])
                                        fieldInfo['version'] = 0
                                        fieldInfo['lastUpdated'] = datetime.now()
                                        fieldInfo['field_id'] = dictField['field_id']
                                        fieldInfo['value'] = value
                                        plantFields.append(fieldInfo)
                                    except:
                                        logger.record("There was a problem validating a integer for a plant's data for zone " + zoneNumber + " and owner " + owner.name)  
                                        continue
                                if dictType == 'boolean':
                                    if field['value'].lower().strip() == 'yes' or field['value'].lower().strip() == 'checked'or field['value'].lower().strip() == 'true':
                                        value = True
                                    else:
                                        value = False
                                    fieldInfo['version'] = 0
                                    fieldInfo['lastUpdated'] = datetime.now()
                                    fieldInfo['field_id'] = dictField['field_id']
                                    fieldInfo['value'] = value
                                    plantFields.append(fieldInfo)
                                if dictType == 'date' and field['value'] != '':
                                    try:
                                        date = field['value'] + ' 00:00:00'
                                        datetimeObject = datetime.strptime(date, "%m/%d/%Y %H:%M:%S")
                                        fieldInfo['version'] = 0
                                        fieldInfo['lastUpdated'] = datetime.now()
                                        fieldInfo['field_id'] = dictField['field_id']
                                        fieldInfo['value'] = datetimeObject
                                        plantFields.append(fieldInfo)
                                    except:
                                        logger.record("There was a problem validating a date for a plant's data for zone " + zoneNumber + " and owner " + owner.name)
                                        continue
                    plant['data'] = plantFields
                    plant['zone'] = int(zoneNumber)
                    plant['plant_id'] = DatabaseUtils.registerPlant(name, scientificName, synonyms)
                    plants.append(PlantEntry.parse_obj(plant))
                # It adds all the plants to the database.
                dictPlants = []
                for plant in plants:
                    dictPlants.append(plant.dict())
                DatabaseUtils.registerEntries(dictPlants)
