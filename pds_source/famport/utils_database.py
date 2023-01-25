import motor.motor_asyncio
import asyncio
import utils_config as ConfigUtils
from datetime import datetime


# For registering schemas.
def registerSchemas(objectDict):
    client = motor.motor_asyncio.AsyncIOMotorClient(ConfigUtils.config.dbURI)
    client.get_io_loop = asyncio.get_running_loop
    database = client.plant_data_service
    schema_collection  = database.famport_registered_schemas
    async def deleteRegistry():
        result = await schema_collection.drop()
    asyncio.run(deleteRegistry())
    print('Deleted schema registry for overwrite ...')
    async def populateRegistry(schemas):
        for item in schemas:
            result = await schema_collection.insert_one(item)
    asyncio.run(populateRegistry(objectDict))
    print('Successfully populated schema registry with new model schemas ...')

# For registering data dictionaries.
def registerDicts(object):
    client = motor.motor_asyncio.AsyncIOMotorClient(ConfigUtils.config.dbURI)
    client.get_io_loop = asyncio.get_running_loop
    database = client.plant_data_service
    dict_collection  = database.data_dictionaries
    # For populating NEW object dictionaries.
    async def populateDataDicts(object):
        result = await dict_collection.insert_one(object)
    # Searches for an existing dictionary. This is useful for updating dictionaries that already exist.
    async def findExistingDict(object):
        id = object['owner_id']
        result = await dict_collection.find_one({'owner_id': id})
        return result
    # Also for updating dictionaries by removing the old one. Note that this doesn't yet conform to our established versioning standards.
    async def deleteOldDict(object):
        id = object['owner_id']
        result = await dict_collection.delete_one({'owner_id': id})
    # Checks to see if a dictionary already exists for the data owner of this ID.
    # If not, it simply adds the data dictionary to the MongoDB collection.
    if asyncio.run(findExistingDict(object)) == None:
        asyncio.run(populateDataDicts(object))
    # If it does, it changes the version and lastUpdated entries for the dictionary and replaces it with the new field values.
    else:
        existingDict = asyncio.run(findExistingDict(object))
        if existingDict['fields'] == object['fields']:
            print('Stored dictionary is the same as the new dictionary. Not updating.')
            return
        else:
            print('Updating dictionary in database...')
            asyncio.run(deleteOldDict(object))
            for newField in object['fields']:
                for oldField in existingDict['fields']:
                    if newField['field_id'] == oldField['field_id'] and newField != oldField:
                        newField['version'] = oldField['version'] + 1
                        newField['lastUpdated'] = datetime.now()
        asyncio.run(populateDataDicts(object))
    print('Successfully imported dictionaries ...')
    print('Check log.txt for any fields that may have been excluded.')

#### NOTE TO SELF FOR TO-DO:
# To make this conform to data versioning standards we have created, the current registerDicts function must be changed:
# 1. lastUpdated and version for the entire dictionary ONLY changes if fields are ADDED or REMOVED.
# 2. lastUpdated and version for each field must be updated ONLY if that specific field changes. Defined by a change to one specific aspect of that field.

def getDataDictionary(owner_id):
    client = motor.motor_asyncio.AsyncIOMotorClient(ConfigUtils.config.dbURI)
    client.get_io_loop = asyncio.get_running_loop
    database = client.plant_data_service
    dict_collection  = database.data_dictionaries
    async def findExistingDict(owner_id):
        result = await dict_collection.find_one({'owner_id': owner_id})
        return result
    return asyncio.run(findExistingDict(owner_id))

def registerPlant(commonName, scientificName, synonyms):
    client = motor.motor_asyncio.AsyncIOMotorClient(ConfigUtils.config.dbURI)
    client.get_io_loop = asyncio.get_running_loop
    database = client.plant_data_service
    plant_collection  = database.plant_library
    async def findExistingPlant(commonName, scientificName, synonyms):
        result = await plant_collection.find_one({'Name': commonName, 'scientificName': scientificName, 'synonyms': synonyms})
        return result
    async def getMaxID():
        result = await plant_collection.find_one(sort=[("plant_id", -1)])
        return result
    async def registerPlant(commonName, scientificName, synonyms, id):
        result = await plant_collection.insert_one({'plant_id': id, 'Name': commonName, 'scientificName': scientificName, 'synonyms': synonyms})
    if asyncio.run(findExistingPlant(commonName, scientificName, synonyms)):
        recognizedPlant = asyncio.run(findExistingPlant(commonName, scientificName, synonyms))
        print('Recognizing plant with ID ' + str(recognizedPlant['plant_id']) + ' ...')
        return int(recognizedPlant['plant_id'])
    else:
        id = asyncio.run(getMaxID())
        if id is None:
            id = 0
        else:
            id = id['plant_id'] + 1
        asyncio.run(registerPlant(commonName, scientificName, synonyms, id))
        print('Successfully registered a plant with ID ' + str(id) + ' ...')
        return id
def registerEntries(objectDict):
    client = motor.motor_asyncio.AsyncIOMotorClient(ConfigUtils.config.dbURI)
    client.get_io_loop = asyncio.get_running_loop
    database = client.plant_data_service
    plant_data_collection  = database.plant_data
    async def populateRegistry(objectDict):
        for item in objectDict:
            result = await plant_data_collection.insert_one(item)
    asyncio.run(populateRegistry(objectDict))
    print('Successfully imported plant data ...')

