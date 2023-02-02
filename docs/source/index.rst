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


Deployment Instructions
==============================================

=================
Deployment on a Remote Server
=================
.. warning::
   This project is under active development.
.. note::
    These instructions were written while using a 64-bit Ubuntu 22.10 Virtual Server and Python 3.10.7 for deployment.

#. **Ensure Python is installed.**

    * You can do this by just running ``python3``.

#. **Install the MongoDB server.**

    * Run ``wget -qO - https://www.mongodb.org/static/pgp/server-6.0.asc | sudo apt-key add -``. You should get 'OK' as a response.
    * Run ``echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/6.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-6.0.list``. You'll need to replace the 'kinetic' part of this bit with the name of the Ubuntu release you are using. You can find the name using ``lsb_release -dc``. For example, Ubuntu 18.04 is named 'bionic'.
    * Get the packages. Run ``apt-get update`` to update your packages list and then ``sudo apt-get install -y mongodb-org``
    * Start MongoDB using ``sudo systemctl start mongod``.
    * It's time to set up a secure login for Mongo. Access the Mongo shell by running ``mongosh``. Use the admin database by running ``use admin`` and then run the following command, replacing the placeholders. **Your password cannot contain : / ? # [ ] @**::

        db.createUser(
        {
        user: "yourusername", 
        pwd: "password", 
        roles:["root"]
        })
     
      * If the admin user has been successfully added, the shell will respond with an ok:1.

#. **Clone the GitHub repository.**

    * Run ``git clone https://github.com/ag-informatics/plant-data-service``. Use credentials as needed. GitHub passwords have switched to Personal Access Tokens.

#. **Extract the Plant Data Service files to wherever you want to run them from.**

    * Just do ``mv plant-data-service/plant-data-service directory/I/Want/To/Run/From`` replacing the last bit with whatever directory you want to house the PDS.

#. **Install dependencies.**

    * Run ``pip install -r requirements.txt`` referring to the requirements.txt included in this repository. The text file should be in the ``plant-data-service`` directory housing the repo. If you do not have Pip installed, you can install it with ``apt install python3-pip``.

#. **Update your Famport config and import the data.**

    * Navigate to where your Famport files are from step 4. In this case, it would be in directory/I/Want/To/Run/From/Famport and the configuration file is config.yml. Replace the default login info for Mongo using the credentials you set up in step 2e within the config.yml Then, import all data using ``python3 main.py --importAllDataAndDictionaries`` in the Famport directory. There will be a lot of printed statements, but if the database connection is successful and things are running smoothly there should be no crashes.

#. **Update your PDS config.**

    * Navigate to where the PDS itself (folder: api_application) is located. Edit the config.yml in the server directory in there to reflect the same database settings as you updated in the previous step.

#. **You're done!**

    * You can confirm that the PDS is working properly by navigating to your IP or domain in your browser. To keep the Python process running, consider using [Screen](https://help.ubuntu.com/community/Screen).

Architecture Overview
==============================================

=================
High-Level Architecture
=================
.. figure:: images/structure.png
    :scale: 50%
    
    Figure: The high-level overview of the architecture of the Plant Data Service.
   
The API
*****************

The PDS API application itself uses `FastAPI <'https://fastapi.tiangolo.com'>`_ FastAPI is a web framework used for creating REST API applications and, despite its newness, has gained popularity due to its asynchronous support and its ease of use. It was selected as the API framework over Django and Flask.
While Django has more built-in features than FastAPI, Django is not suited for NoSQL databases or linked data structures.
Flask is suited for basically however you want to organize your data, but generally takes longer to develop basic functionalities and it lacks a lot of things "out of the box".

Modules and tools included with FastAPI
The FastAPI has a toolbox of different modules and standards that you can use together for a robust application. Some of these important features include:

* `SwaggerUI <'https://swagger.io/tools/swagger-ui/'>`_: SwaggerUI is used to create beautiful and highly functional documentation of functions and defined object schemas automatically. 
* `Pydantic <'https://docs.pydantic.dev/'>`_: Pydantic is used for object relational mapping and data validation. It can be used to create schemas that define objects used in API responses and can be used in conjunction with SwaggerUI for extremely in-detail auto documentation.
* `OpenAPI <'https://www.openapis.org'>`_: OpenAPI is a set of standards used for easy interfacing with RESTful APIs. It used to be a part of Swagger before becoming its own project.

The webserver used for the API application
-----------------
The API runs on `Uvicorn <'https://uvicorn.org'>`_. Uvicorn is an ASGI (Asynchronous Server Gateway Interface) server for Python applications. Uvicorn allows for quick, asynchronous handling of requests. Generally speaking, Uvicorn is the recommended webserver for FastAPI applications.

Data Structuring and Database Management System Selection
*****************

Why we chose to use a NoSQL database
-----------------

It was determined earlier on in the development and design process that NoSQL was the way to go for storing data used by the PDS. Why?

#. NoSQL databases are highly flexible, and it's easy to link data together in a NoSQL database. For our purposes, NoSQL is a better option for representing plant data in a variety of contexts. This schemaless setup is also important for a system that uses data from many owners that all structure their data slightly differently.
#. They're easier to manage than a SQL database. While SQL databases work well for rigid data structures or large development teams, the level of management they require is not ideal for the PDS project.

Essentially, SQL Database Management Systems are based on a schema that *must* be adhered to. Our NoSQL DBMS, MongoDB, simply stores a collection of JSON documents within "collections" (analogous to separate databases within the same SQL server). These documents all have unique IDs and do not have to follow any specific defined schema. 


Why we chose MongoDB as our Database Management System (DBMS)
-----------------

A couple DBMSs were considered during the early phases of development. One promising DBMS was `OrientDB <https://orientdb.org>`_ , but Orient proved to be outdated for current versions of its Python tool and its related dependencies.
We settled with `MongoDB <https://mongodb.com>`_ since it is widely used (and more reliable than Orient). As a NoSQL DBMS, MongoDB stores collections of "documents" with non-rigid schemas. The flexibility of data storage allows data to be linked together.


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