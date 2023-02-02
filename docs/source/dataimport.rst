Importing Data: Famport
==============================================

Famport (**F**ast**A**PI **M**ongoDB Im**port**er) is a component of the data import and validation process of the Plant Data Service. It offers a set of functions that can be used to bulk import raw data and data dictionaries into MongoDB to be accessed by the API.

Use
*****************

To use Famport, you run the main.py found in the /famport directory. There's a couple different options for data import.
Options that may overwrite or delete anything stored in MongoDB require confirmation after running the option.

* ``python3 main.py --help`` gives you a list of possible functional arguments.
* ``python3 main.py --importAllDataAndDictionaries`` will import all data and data dictionaries as defined in the famport config.yml.
* ``python3 main.py ---importDataDictionaries`` will import only data dictionaries as defined in the famport config.yml.

Configuration
*****************
Configuration is found in the config.yml, which is commented extensively to explain what each setting does.

The configuration has options for defining each data owner and their respective raw data inputs and data dictionaries, which must all be placed in the ```/famport/import_resources/``` directory.

