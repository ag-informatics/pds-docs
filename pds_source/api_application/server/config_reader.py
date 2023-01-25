# Importing for getting configuration values.
import yaml
from yaml.loader import SafeLoader


# GETTING CONFIGURATION VALUES  ----------------------------------------------------------
def readConfig():
    with open('server/config.yml','r') as configFile:
        config = yaml.load(configFile, Loader = SafeLoader)
    return config
# The entire configuration object.

class config:
    # All database-related stuff here. For connecting to MongoDB server.
    dbHost = readConfig()['host']
    dbPort = str(readConfig()['port'])
    dbUser = readConfig()['username']
    dbPass = readConfig()['password']
    if dbUser == "" and dbPass == "":
        dbURI = "mongodb://"+ dbHost +":"+ dbPort
    else:
        dbURI = "mongodb://" +  dbUser + ":" + dbPass + "@" + dbHost + ":" + dbPort + "/?authSource=admin"
    # For getting data owner dictionary collection from the config.