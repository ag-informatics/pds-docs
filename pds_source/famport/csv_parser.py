import csv

# Reads the CSV file and returns a dictionary in the format:
def csvRead(csvFile):
    csvData = {}
    # Opened with utf-8-sig encoding to remove the weird little ï»¿ BOM characters
    with open(csvFile, encoding ='utf-8-sig') as readFile:
        csvReader = csv.DictReader(readFile, delimiter = ',')
        for row in csvReader:
            for column, value in row.items():
                csvData.setdefault(column,[]).append(value)
    return csvData

# Sorts through the CSV file to create data that is sorted and ready to be manipulated.
def sort(dataDict):
    listOfLists = []
    for variable in list(dataDict.keys()):
        listOfLists.append(dataDict[variable])
    sortedData = []
    index = 0
    for variable in listOfLists[0]:
        dataArray = []
        for line in listOfLists:
            dataArray.append(line[index])
        index += 1
        sortedData.append(dataArray)
    return sortedData

# Combines the two above functions and returns the sorted data from a CSV file.
def parseCSV(csvFile):
    return sort(csvRead(csvFile))

# Counts lines in a CSV file.
def getEntries(csvFile):
    with open(csvFile,encoding ='utf-8-sig') as f:
        reader = csv.reader(f, delimiter = ',')
        data = list(reader)
        numberOfEntries = len(data) - 1 # The - 1 accounts for a row in the data set belonging to field names.
    return numberOfEntries
