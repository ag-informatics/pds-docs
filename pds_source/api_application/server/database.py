import motor.motor_asyncio
import asyncio
import server.config_reader as Config
import json
from bson import json_util

client = motor.motor_asyncio.AsyncIOMotorClient(Config.config.dbURI)
client.get_io_loop = asyncio.get_running_loop
database = client.plant_data_service
dict_collection = database.data_dictionaries
plant_collection = database.plant_data

def DictHelper(data):
    return {
       'dictionaries': data
    }

def PlantHelper(data):
    return {
        'plants': data
    }

def retrieveDictionaries():
    async def findAllDicts():
        dicts = []
        async for document in dict_collection.find({}, {'_id': False}):
            dicts.append(document)
        return dicts
    return DictHelper(asyncio.run(findAllDicts()))

def retrieveAllDataOfPlant(id):
    async def findAllDataOfPlant(name):
        plants = []
        async for plant in plant_collection.find({'plant_id': name}):
            plants.append(plant) 
        return plants
    plants = asyncio.run(findAllDataOfPlant(id))
    for plant in plants:
        del plant['_id']
    dictionaries = retrieveDictionaries()
    for plant in plants:
        dataPoints = []
        for data in plant['data']:
            newData = {}
            for dictionary in dictionaries['dictionaries']:
                for field in dictionary['fields']:
                    if field['field_id'] ==  data['field_id']:
                        machineReadableName = field['machineReadableName']
                        description = field['description']
                        if field['dataType'] == 'enum':
                            values = []
                            for item in data['value']:
                                try:
                                    values.append(field['options'][item])
                                except:
                                    return({'error': 'issue with plant ' + str(plant['plant_id']) + ' and field ' + str(field['field_id'])})
                            if len(values) == 1:
                                values = values[0]
                            newData['name'] = machineReadableName
                            newData['description'] = description
                            newData['value'] = values
                            dataPoints.append(newData)
                        else:
                            newData['name'] = machineReadableName
                            newData['description'] = description
                            newData['value'] = data['value']
                            dataPoints.append(newData)
        plant['data'] = dataPoints
    return PlantHelper(plants)
    
def retrieveCoverCropsFromPlant(id):
    async def findAllDataOfPlant(name):
        plants = []
        async for plant in plant_collection.find({'plant_id': name}):
            plants.append(plant) 
        return plants
    plants = asyncio.run(findAllDataOfPlant(id))
    ccTags = ["Goals", "CoverCrop", "Plant"]
    for plant in plants:
        del plant['_id']
    dictionaries = retrieveDictionaries()
    for plant in plants:
        dataPoints = []
        for data in plant['data']:
            newData = {}
            for dictionary in dictionaries['dictionaries']:
                for field in dictionary['fields']:
                    ccField = False
                    if field['field_id'] == data['field_id']:
                        try:
                            for tag in field['tags']:
                                if tag in ccTags:
                                    ccField = True
                        except:
                            continue
                        if ccField == True:
                            machineReadableName = field['machineReadableName']
                            description = field['description']
                            if field['dataType'] == 'enum':
                                values = []
                                for item in data['value']:
                                    try:
                                        values.append(field['options'][item])
                                    except:
                                        return({'error': 'issue with plant ' + str(plant['plant_id']) + ' and field ' + str(field['field_id'])})
                                if len(values) == 1:
                                    values = values[0]
                                newData['name'] = machineReadableName
                                newData['description'] = description
                                newData['value'] = values
                                dataPoints.append(newData)
                            else:
                                newData['name'] = machineReadableName
                                newData['description'] = description
                                newData['value'] = data['value']
                                dataPoints.append(newData)
        plant['data'] = dataPoints
    return PlantHelper(plants)
