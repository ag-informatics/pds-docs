.. Plant Data Service documentation master file, created by
   sphinx-quickstart on Wed Jan 25 17:17:53 2023.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

PDS Documentation
==============================================
**Welcome to the Plant Data Service Documentation!**

.. image:: images/tree.png
   :width: 150
   :align: right

The Plant Data Service is an open-source plant data API. It was inspired by the growing need for information sharing within agriculture and was created to meet the needs of the National Cover Crop Councils.

You can demo the PDS `here <http://142.93.60.97/>`_ .


Famport: What it is, Structure, and Code
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

What Comes Next
==============================================

**Geographic Matching:**
To meet original needs, the Plant Data Service will support the matching of plant data to geographic locations. These locations will determine what data is shown and from what data owner and will support the coordinate, county, state, and region levels.

**Functionality Expansion:**
More functions will be added to the Plant Data Service. These functions will support requests for plant searches and domain-specific data (e.g. a function that supports the look up of agronomic, phenologic, or stress-related data for a plant given a geographic location).

**Administrative Panel Creation:**
Since previous attempts to find an adequate data administration panel have failed, scoping will be conducted to identify needs for an administration panel that allows data owners to edit, create, and delete data stored within the PDS.

**Multi-Dictionary Support:**
Currently, famport only allows one data dictionary per owner. Multi-dictionary support will be necessary in the near future.

.. toctree::
   :maxdepth: 1

   deployment
   architecture