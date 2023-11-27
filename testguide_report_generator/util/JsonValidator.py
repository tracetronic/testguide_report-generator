# Copyright (c) 2023 TraceTronic GmbH
#
# SPDX-License-Identifier: MIT

# -*- coding: utf-8 -*-

"""
This module contains the JsonValidator class.
"""

import json
import os

import jsonschema

DEFAULT_JSON_SCHEMA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..",
                                        "schema", "schema.json")


class JsonValidator:
    """
    Validator for the Json2Atx file.
    """

    def __init__(self, json_schema_file_path: str = DEFAULT_JSON_SCHEMA_PATH):
        """
        Constructor.

        :param json_schema_file_path: path to Json schema file
        :type json_schema_file_path: str
        """

        with open(json_schema_file_path, 'r', encoding='utf-8') as file:
            self.__schema = json.loads(file.read())

    def validate_file(self, json_file_path: str):
        """
        Validates the given json file against the schema.

        :param json_file_path: path to generated json schema
        :type json_file_path: str
        :return: true if the validation was successful, otherwise false
        :rtype: boolean
        """

        with open(json_file_path, 'r', encoding='utf-8') as file:
            json_content = json.loads(file.read())

        validator = jsonschema.Draft7Validator(self.__schema)
        errors = sorted(validator.iter_errors(json_content), key=lambda e: e.path)
        for error in errors:
            for sub_error in sorted(error.context, key=lambda e: e.schema_path):
                print(list(sub_error.schema_path), sub_error.message, sep=", ")

        return len(errors) == 0

    def validate_json(self, json_object: dict):
        """
        Validates the given json object against the schema.

        :param json_object: dictionary which represents json formatted data
        :type json_object: dict
        :return: true if the validation was successful, otherwise false
        :rtype: boolean
        """

        validator = jsonschema.Draft7Validator(self.__schema)
        errors = sorted(validator.iter_errors(json_object), key=lambda e: e.path)
        for error in errors:
            for sub_error in sorted(error.context, key=lambda e: e.schema_path):
                print(list(sub_error.schema_path), sub_error.message, sep=", ")

        return len(errors) == 0
