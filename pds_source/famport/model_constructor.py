import logger
import re
import os
import csv_parser as CSVParser
import utils_formatting as FormatUtils
import utils_database as DatabaseUtils

# Gets a list of all models mentioned in the data dictionary
def getModelList(sortedData):
    listOfModels = [] # A list of all models defined in the data dictionary
    for variable in sortedData:
        model = variable[5]
        if model not in listOfModels and model.strip() != "":
            listOfModels.append(model)
    return listOfModels 

# Translates the data type into a valid Python declaration
def dataTypeTranslate(dataType):
    if dataType.lower() == "string":
        dataType = "str"
    elif dataType.lower() == "float":
        dataType = "float"
    elif dataType.lower() == "date":
        dataType = "datetime.datetime"
    elif dataType.lower() == "integer":
        dataType = "int"
    elif dataType.lower() == "boolean":
        dataType = "bool"
    elif dataType.lower() == "enum" or dataType.lower() == "enumeration":
        dataType = "enum"
    else:
        dataType = "!"
    return dataType

# Creates the dict definitions for non-enumeration variables.
# This is necessary to go along with OpenAPI standards and still provide the metadata we want to provide.
def createNonEnumField(dataType, variableName, model):
    firstLine= "\nclass " + variableName + "(TypedDict):\n"
    secondLine = "  value: " + dataType + "\n"
    thirdLine = "  fieldVersion: int \n"
    fourthLine = "  fieldLastRevised: datetime\n"
    fullStr = firstLine + secondLine + thirdLine + fourthLine
    return (fullStr, model)

# Creates the enum class definitions for enumeration variables.
def createEnumField(variableName, choices, model):
    choiceLines = []
    firstLine = "\nclass " + variableName + "(str,Enum):\n"
    for choice in choices:
        cleanName = FormatUtils.translateToMachineRead(choice)
        line = "   " + cleanName + " = '''" + choice + "'''\n"
        choiceLines.append(line)
    fullStr = firstLine
    for choice in choiceLines:
        fullStr += choice
    return (fullStr, model)

# Creates the normal Pydantic declarations as seen in the BaseModel examples
def writeDeclaration(dataType, machineReadableName, description, required, model):
    if required == "0" or required == "no" or required == "false" or required == "" or required == " ":
        pydanticLineStr = "   " + machineReadableName + ": " + dataType + " | None"
        # If a description is given for the variable it will be added here
        if description != "   " and description != "":
            pydanticLineStr = pydanticLineStr + " = Field(default = None, description = '''" + description + "''')\n"
    else:
        pydanticLineStr = "   " + machineReadableName + ": " + dataType 
        if description != "   " and description != "":
            pydanticLineStr = pydanticLineStr + " = Field(description = '''" + description +"''')\n"
    return (pydanticLineStr,model, machineReadableName)


def constructModels(data, name):
    sortedData = data
    models = getModelList(sortedData)
    listOfDeclarations = []                          # The list of Pydantic declaration lines for the base model
    listOfEnumDeclarations = []                      # The list of enumeration declarations
    listOfDictDeclarations = []                      # The list of non-enumeration declarations
    for row in sortedData:
        machineReadableName = row[1]                 # The machine-readable name of the field
        variableName = row[0]                        # The human-readable name of the field
        dataType = dataTypeTranslate(row[3])         # Data type of the field
        enumChoices = row[4].split(",")              # Choices for enumerations
        modelCategory = row[5]                       # Model the variable is associated with
        required = row[6]                            # Whether or not the field is required for creating a new entry in the collection
        description = row[2]                         # Description describing the field

        # Checks to ensure that the field has a valid machine readable name
        if machineReadableName == '':
            errorResp = "Variable '" + variableName + "' has no machine-readable variable name associated with it."
            errorRespAdd = "'" + variableName + "' was not added to the " + modelCategory + " model."
            logger.record(errorResp)
            logger.record(errorRespAdd)
            continue
        # Checks to ensure that the field has a valid model category it is associated with
        if modelCategory == '':
            errorResp = "Variable '" + machineReadableName + "' has no model category associated with it."
            errorRespAdd = "'" + machineReadableName + "' will not be added!"
            logger.record(errorResp)
            logger.record(errorRespAdd)
            continue
        # Checks to ensure that the field has a valid data type
        if dataType == "!":
            errorResp = "Variable '" + machineReadableName + "' has an invalid or unknown data type assigned to it."
            errorRespAdd = "'" + machineReadableName + "' was not added to the " + modelCategory + " model!"
            logger.record(errorResp)
            logger.record(errorRespAdd)
            continue
        
        # Changes the data type to refer to the respective enumeration or dictionary entries.
        if dataType == "enum":
            dataTypeDec = FormatUtils.createEnumName(machineReadableName)
            dataTypeDecDict = FormatUtils.createDictName(machineReadableName)
            listOfEnumDeclarations.append(createEnumField(dataTypeDec,enumChoices,modelCategory))
            listOfDictDeclarations.append(createNonEnumField(dataTypeDec,dataTypeDecDict,modelCategory))
            listOfDeclarations.append(writeDeclaration(dataTypeDecDict, machineReadableName, description, required, modelCategory))
        else:
            dataTypeDec = machineReadableName.replace("_", "") + "Dict"
            listOfDictDeclarations.append(createNonEnumField(dataType,dataTypeDec,modelCategory))
            listOfDeclarations.append(writeDeclaration(dataTypeDec, machineReadableName, description, required, modelCategory))
        

    objectList = [] # Used for entering the list of model files to a registry on MongoDB for data import.

    # Goes through the model list and writes the appropriate Python declarations to each model.
    for model in models:
        modelNameUpper = model.capitalize()   # For the BaseModel name
        modelNameLower = model.lower()        # For the file name
        modelDeclarations = []                # Pydantic declarations
        modelDicts = []                       # Defined dictionaries for each non-enum variable
        modelEnums = []                       # Defined choices for each enum variable
        for item in listOfDeclarations:
            if item[1] == model:
                modelDeclarations.append(item[0])
        for item in listOfDictDeclarations:
            if item[1] == model:
                modelDicts.append(item[0])
        for item in listOfEnumDeclarations:
            if item[1] == model:
                modelEnums.append(item[0])
        modelFileName = modelNameLower + "_" + name + ".py"
        path = os.path.dirname(os.path.dirname( __file__ )) + '\\famport\dynamic_models\\'
        modelFile = open(path + modelFileName, "w")
        header = f"""from pydantic import BaseModel, Field
from typing import List
from datetime import date, datetime, time, timedelta
from enum import Enum
from typing_extensions import TypedDict
"""
        modelFile.write(header)

        for line in modelEnums:
            modelFile.write(line)
        for line in modelDicts:
            modelFile.write(line)
        
        objectName =  modelNameUpper + name + "Schema"
        modelFile.write("\nclass " + modelNameUpper + name + "Schema(BaseModel):\n")
        modelFile.write("   lnk_id: int\n")
        modelFile.write("   # These next two variables, docVersion and docLastRevised, are for versioning on the document level.\n")
        modelFile.write("   docVersion: int\n")
        modelFile.write("   docLastRevised: datetime\n")
        
        for line in modelDeclarations:
            modelFile.write(line)

        footer = """
    # Used for creating an object with this schema
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
""" 
        modelFile.write(footer)

        # For registering schemas into the database.
        listOfVariables = []
        for item in listOfDeclarations:
            if item[1] == model:
                listOfVariables.append(item[2])
        objectList.append({'fileName': modelFileName, 'schemaObject': objectName, 'machineReadableNames': listOfVariables})   
    DatabaseUtils.registerSchemas(objectList)

def getModelList(sortedData):
    listOfModels = [] # A list of all models defined in the data dictionary
    for variable in sortedData:
        model = variable[5]
        if model not in listOfModels and model.strip() != "":
            listOfModels.append(model)
    return listOfModels 

# Translates the data type into a valid Python declaration
def dataTypeTranslate(dataType):
    if dataType.lower() == "string":
        dataType = "str"
    elif dataType.lower() == "float":
        dataType = "float"
    elif dataType.lower() == "date":
        dataType = "datetime.datetime"
    elif dataType.lower() == "integer":
        dataType = "int"
    elif dataType.lower() == "boolean":
        dataType = "bool"
    elif dataType.lower() == "enum" or dataType.lower() == "enumeration":
        dataType = "enum"
    else:
        dataType = "!"
    return dataType

# Creates the dict definitions for non-enumeration variables.
# This is necessary to go along with OpenAPI standards and still provide the metadata we want to provide.
def createNonEnumField(dataType, variableName, model):
    firstLine= "\nclass " + variableName + "(TypedDict):\n"
    secondLine = "  value: " + dataType + "\n"
    thirdLine = "  fieldVersion: int \n"
    fourthLine = "  fieldLastRevised: datetime\n"
    fullStr = firstLine + secondLine + thirdLine + fourthLine
    return (fullStr, model)

# Creates the enum class definitions for enumeration variables.
def createEnumField(variableName, choices, model):
    choiceLines = []
    firstLine = "\nclass " + variableName + "(str,Enum):\n"
    for choice in choices:
        cleanName = FormatUtils.translateToMachineRead(choice)
        line = "   " + cleanName + " = '''" + choice + "'''\n"
        choiceLines.append(line)
    fullStr = firstLine
    for choice in choiceLines:
        fullStr += choice
    return (fullStr, model)

# Creates the normal Pydantic declarations as seen in the BaseModel examples
def writeDeclaration(dataType, machineReadableName, description, required, model):
    if required == "0" or required == "no" or required == "false" or required == "" or required == " ":
        pydanticLineStr = "   " + machineReadableName + ": " + dataType + " | None"
        # If a description is given for the variable it will be added here
        if description != "   " and description != "":
            pydanticLineStr = pydanticLineStr + " = Field(default = None, description = '''" + description + "''')\n"
    else:
        pydanticLineStr = "   " + machineReadableName + ": " + dataType 
        if description != "   " and description != "":
            pydanticLineStr = pydanticLineStr + " = Field(description = '''" + description +"''')\n"
    return (pydanticLineStr,model, machineReadableName)