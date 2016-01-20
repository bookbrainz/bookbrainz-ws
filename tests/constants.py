# -*- coding: utf8 -*-
""" In this module there are different constants used in web-service tests

    The most important ones:

    DEFAULT_MAX_QUANTITY is a maximum number of entities that could be generated
    for each entity type

    DEFAULT_MAX_STRING_SIZE is a maximum number of characters in a random
    unicode strings that are generated for generating sample data purposes

    NEW_ALIASES_MAX_COUNT is a maximum number of aliases that could be generated
    for each entity

    If you want the tests to run faster, just lower them.

    Note that PUT_TESTS_GOOD_COUNT should be set well above DEFAULT_MAX_QUANTITY
    on purpose to make entities be changed more than once.

"""
DEFAULT_MAX_QUANTITY = 30
DEFAULT_MAX_STRING_SIZE = 65

LANGUAGES_COUNT = 25
GENDERS_COUNT = 25

EDITION_FORMATS = 25
EDITION_STATUSES = 25

NEW_ALIASES_MAX_COUNT = 20
NEW_LANGUAGES_MAX_COUNT = 20
NEW_IDENTIFIERS_MAX_COUNT = 20
RELATIONSHIP_TEXTS_MAX_COUNT = 20
USER_LANGUAGES_MAX_COUNT = 20

GET_BBID_TESTS_GOOD_COUNT = 15
GET_BBID_TESTS_BAD_COUNT = 15

GET_LIST_TESTS_COUNT = 3

POST_TESTS_GOOD_COUNT = 25
POST_TESTS_BAD_COUNT = 25

PUT_TESTS_GOOD_COUNT = 80
PUT_TESTS_BAD_COUNT = 20
