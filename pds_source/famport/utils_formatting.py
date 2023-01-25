# This file includes some often-used functions that don't fit anywhere else.

# STANDARD STRING MANIPULATION FUNCTIONS ----------------------------------------------------------
# Creates class names for Pydantic models.
# Mainly putting here for naming standardization throughout famport. 
# Primarily used by model_constructor.py
def createEnumName(text):    # For creating Enum classes in Pydantic.
    text = translateToMachineRead(text)
    return text + 'Enum'

def createDictName(text):    # For creating Dict classes in Pydantic.
    text = translateToMachineRead(text)
    return text + 'Dict'

def translateToMachineRead(value):          # For translating Enum options into something machine-readable variable names.
    translatedText = value
    translatedText = translatedText.lower()
    translatedText = translatedText.replace(' ', '_')
    text = ''
    for character in translatedText:
        if character.isalpha():
            text += character
        if character == '_':
            text += character
    translatedText = text.strip()
    return translatedText
