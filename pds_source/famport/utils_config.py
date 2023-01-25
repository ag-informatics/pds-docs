# Importing for getting configuration values.
import yaml
from yaml.loader import SafeLoader
# Importing data owner object.
from static_models.dataowner import Owner

# GETTING CONFIGURATION VALUES  ----------------------------------------------------------
def readConfig():
    with open('config.yml','r') as configFile:
        config = yaml.load(configFile, Loader = SafeLoader)
    return config

# Getting a definition for each data owner.
# This maps config options to the data owner schema defined in static_models.
def defineOwnersFromConfig():
    ownerObjectList = []                        # A list for storing owner objects to pass to the config class.
    ownerIndex = 0
    dataOwners = readConfig()['dataowners']     # Pulls data owner settings from the config.yml.
    for entry in dataOwners:
        zoneList = []
        name = next(iter(entry)) 
        # Any line that says entry["something"] is mapping a value from the config to a specific variable defined in the Owner schema.
        entry["name"] = name
        entry["owner_id"] = ownerIndex
        objectIndex = 0
        for object in entry[name]:
            if next(iter(object)) == 'Zones':
                for zone in entry[name][objectIndex]['Zones']:
                    zoneEntry = {"zone": zone["zone_number"], "importFile": zone["importfile"]}  # Maps each individual zone
                    zoneList.append(zoneEntry)
                entry["zones"] = zoneList
            if next(iter(object)) == "Website":
                entry["website"] = entry[name][objectIndex]['Website']
            if next(iter(object)) == "States":
                entry["states"] = entry[name][objectIndex]['States']
            if next(iter(object)) == "DataDictionary":
                entry["dataDictionary"] = entry[name][objectIndex]['DataDictionary']
            objectIndex += 1
        ownerObjectList.append(Owner.parse_obj(entry))
        ownerIndex += 1
    return ownerObjectList




# The entire configuration object.
class config:
    # All database-related stuff here. For connecting to MongoDB server.
    dbHost = readConfig()['host']
    dbPort = str(readConfig()['port'])
    dbUser = readConfig()['username']
    dbPass = readConfig()['password']
    # URI for connecting to MongoDB using PyMongo.
    if dbUser == "" and dbPass == "":
        dbURI = "mongodb://"+ dbHost +":"+ dbPort
    else:
        dbURI = "mongodb://" +  dbUser + ":" + dbPass + "@" + dbHost + ":" + dbPort + "/?authSource=admin"
    # For getting data owner dictionary collection from the config.
    dataOwners = defineOwnersFromConfig()
