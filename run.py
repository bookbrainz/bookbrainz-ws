#!/usr/bin/env python2.7
# -*- coding: utf8 -*-

# Copyright (C) 2014-2015  Ben Ockmore

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.


""" This script will start the webservice, provided the environment is
correctly set up. The path to a config file must be passed to the script as a
command-line argument, and additional arguments may be passed - see script
help.
"""


import argparse
import os

from bbws import create_app

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='BookBrainz Web Service')
    parser.add_argument(
        'config', type=str,
        help='the configuration file used to initialize the application'
    )
    parser.add_argument('-d', '--debug', action='store_true')
    parser.add_argument('--host', type=str, default='0.0.0.0',
                        help='the desired hostname/IP for the server')
    parser.add_argument('--port', type=int, default=5000,
                        help='the desired port number for the server')

    args = parser.parse_args()

    # Use absolute path here, otherwise config.from_pyfile makes it invalid.
    app = create_app(os.path.abspath(args.config))
    app.run(debug=args.debug, host=args.host, port=args.port)
