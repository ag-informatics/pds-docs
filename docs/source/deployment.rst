Deployment Instructions
==============================================

=================
Deployment on a Remote Server
=================

.. note::
    These instructions were written while using a 64-bit Ubuntu 22.10 Virtual Server for deployment.

#. **Ensure Python is installed.**

    * You can do this by just running ``python3``. Note its version. I am using Python 3.10.7.

#. **Install the MongoDB server.**

    * Run ``wget -qO - https://www.mongodb.org/static/pgp/server-6.0.asc | sudo apt-key add -``. You should get 'OK' as a response.
    * Run ``echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/6.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-6.0.list``. You'll need to replace the 'kinetic' part of this bit with the name of the Ubuntu release you are using. You can find the name using ``lsb_release -dc``. For example, Ubuntu 18.04 is named 'bionic'.
    * Get the packages. Run ``apt-get update`` to update your packages list and then ``sudo apt-get install -y mongodb-org``
    * Start MongoDB using ``sudo systemctl start mongod``.
    * It's time to set up a secure login for Mongo. Access the Mongo shell by running ``mongosh``. Use the admin database by running ``use admin`` and then run the following command, replacing the placeholders. **Your password cannot contain : / ? # [ ] @** ::
    db.createUser(
   {
       user: "yourusername", 
       pwd: "password", 
       roles:["root"]
   })
     
If the admin user has been successfully added, the shell will respond with an ok:1.

#. **Clone the GitHub repository.**

    * Run ``git clone https://github.com/ag-informatics/plant-data-service``. Use credentials as needed. GitHub passwords have switched to Personal Access Tokens.

#. **Extract the Plant Data Service files to wherever you want to run them from.**

    * Just do ``mv plant-data-service/plant-data-service directory/I/Want/To/Run/From`` replacing the last bit with whatever directory you want to house the PDS.

#. **Install dependencies.**

    * Run ``pip install -r requirements.txt`` referring to the requirements.txt included in this repository. The text file should be in the ``plant-data-service`` directory housing the repo. If you do not have Pip installed, you can install it with ``apt install python3-pip``.

#. **Update your Famport config and import the data.**

Navigate to where your Famport files are from step 4. In this case, it would be in directory/I/Want/To/Run/From/Famport and the configuration file is config.yml. Replace the default login info for Mongo using the credentials you set up in step 2e within the config.yml Then, import all data using ``python3 main.py --importAllDataAndDictionaries`` in the Famport directory. There will be a lot of printed statements, but if the database connection is successful and things are running smoothly there should be no crashes.

#. **Update your PDS config.**

Navigate to where the PDS itself (folder: api_application) is located. Edit the config.yml in the server directory in there to reflect the same database settings as you updated in the previous step.

#. **You're done!**

You can confirm that the PDS is working properly by navigating to your IP or domain in your browser. To keep the Python process running, consider using [Screen](https://help.ubuntu.com/community/Screen).
