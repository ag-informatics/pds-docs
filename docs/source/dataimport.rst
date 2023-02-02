Importing Data
==============================================

Famport (**F** ast **A** PI **M** ongoDB Im **port** er) is a component of the data import and validation process of the Plant Data Service. It offers a set of functions that can be used to bulk import raw data and data dictionaries into MongoDB to be accessed by the API.

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

The configuration has options for defining each data owner and their respective raw data inputs and data dictionaries, which must all be placed in the ``/famport/import_resources/`` directory.

Data Dictionary Requirements
*****************

Famport requires that the data dictionary follows a specific set of requirements. Famport only accepts data dictionaries in CSV format and it is primarily based on the data dictionary requirements listed by the USDA's Ag Data commons (more on that `here <'https://data.nal.usda.gov/data-dictionary-examples'>`_).

.. list-table:: Data Dictionary Requirements for Famport
   :header-rows: 1

   * - Human-Readable Name
     - Machine-Readable Name
     - Description
     - Data Type
     - Enumeration Options
     - Collection
     - Requirement
   * - **Accepted values:**: Any string.
     - **Accepted values:**: Any machine-readable string. Should not contain spaces or special characters. Optimally, use only numbers, alphabetical characters, and underscores.
     - **Accepted values:**: Any string. 
     - **Accepted values:**: Must be one of the following to define data types - "string", "float", "date", "integer", "boolean", "enum" 
     - **Accepted values:** Any comma-separated strings. Only applies if the data type is "enum". Formatted in the CSV with all options encased in double quotes.
     - **Accepted values:** Any string.
     - **Accepted values:** For a field to NOT be required, this can be left empty or have "false" or "no". All other values are determined as stating that the field is required for the model.

Raw Data Requirements
*****************
As with data dictionaries, Famport only accepts raw data in CSV format. When processing raw data, Famport will attempt to validate or force data types. If these attempts fail, Famport will skip over the piece of data and move on to the next. If you see that not all of your data is being included, you should check your ``log.txt``. 

Most data types are handled pretty simply. However, the handling of enumerations is nuanced. Since Famport imports data into Mongo that pseudo-links back to the appropriate data-dictionary, enumerations are handled in a way that allows for changes in the data dictionary within Mongo to be expressed immediately within requests. That being said, a change in an enumeration option within this data dictionary will result in a change in the associated enumeration option in an API call.

Famport will attempt to match enumerations provided in the raw data with ones in the data dictionary. Its process looks like:

#. If the enumeration option is an integer, then it will enforce integer typing and turn it into an index pointing to an enumeration option array in the data dictionary.
#. Otherwise, Famport will try to match a lowercase and whitespace-stripped version of the enumeration directly to an option in the data dictionary enumeration option array.
#. If (1) and (2) fail, Famport will try to regex match the enumeration option to an option in the data dictionary enumeration option array.

The result is that each enumeration selection in the raw data will become an index that acts as an identifier pointing to a specific option in the enumeration option array within the data dictionary.