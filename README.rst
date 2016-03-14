BookBrainz Web Service
======================

This is the Python version of the Web Service.

Installing
----------
Please follow the instructions in the bookbrainz-schema repository to set up
the database.

Then, install the webservice's dependencies by running:

    pip install -r requirements.txt

Also ensure that you also have a recent version of Redis installed.

Then, copy the configuration file config/deploy.py.example to config/deploy.py,
and edit it to reflect your environment. Then, finally, launch the webservice
by running:

    python run.py config/deploy.py

Or, for debug mode:

    python run.py -d config/deploy.py
