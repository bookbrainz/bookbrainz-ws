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

""" This script stores a randomly selected publication GID in the webservice
redis cache, which can be used to return a "book of the week" result for the
site homepage.
"""

import random

import redis
from bbschema import Entity, EntityRevision, EntityTree, PublicationData
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql.expression import func


def main(conn_string):
    r = redis.Redis(host='localhost', port=6379)
    engine = create_engine(conn_string, echo=True)

    Session = sessionmaker(bind=engine)
    session = Session()

    # First, generate a query to select all publications from the database
    q = session.query(Entity).join(EntityRevision, Entity.master_revision)
    q = q.join(EntityTree).join(PublicationData)

    random_selection = []
    while not random_selection:
        # Now, extend the query to compile a selection of 1000 randomly
        # selected publications, with a randomly selected random threshold.
        random_selection = q.filter(
            func.random() < random.random()
        ).limit(1000).all()

    # Randomly select a publication from the shortlist
    botw = random_selection[random.randint(0, len(random_selection) - 1)]

    print "Book of the Week GID:", botw.gid
    r.set('botw', botw.gid)


if __name__ == '__main__':
    import sys
    main(sys.argv[1])
