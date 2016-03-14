# BookBrainz Web Service
[![Build Status](https://travis-ci.org/bookbrainz/bookbrainz-ws.svg?branch=master)](https://travis-ci.org/bookbrainz/bookbrainz-ws)
[![Code Climate](https://codeclimate.com/github/bookbrainz/bookbrainz-ws/badges/gpa.svg)](https://codeclimate.com/github/bookbrainz/bookbrainz-ws)
[![Coverage Status](https://coveralls.io/repos/bookbrainz/bookbrainz-ws/badge.svg?branch=master&service=github)](https://coveralls.io/github/bookbrainz/bookbrainz-ws?branch=master)

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
