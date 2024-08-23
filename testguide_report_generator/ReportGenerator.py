# Copyright (c) 2023-2024 tracetronic GmbH
#
# SPDX-License-Identifier: MIT

"""
This module contains the JsonGenerator class.
"""

import json
import os

from zipfile import ZipFile, ZIP_DEFLATED
from testguide_report_generator.model.TestSuite import TestSuite
from testguide_report_generator.model.TestCase import TestCase
from testguide_report_generator.model.TestCaseFolder import TestCaseFolder
from testguide_report_generator.util.JsonValidator import JsonValidator

DEFAULT_JSON_SCHEMA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "schema",
                                        "schema.json")


class Generator:
    """
    This class is responsible for the creation of the `.zip` file containing the test report and
    possible artifacts, which can be uploaded to test.guide. An object of type
    :class:`TestSuite<testguide_report_generator.TestSuite.TestSuite>` is necessary, containing the
    information about all testcases in a format compliant with the `test.guide schema.json`. It
    is possible that the `.json` generated from the TestSuite object is not compliant with the
    schema, for instance, if the suite does not contain any testcases. For further information,
    please conduct the README.
    """


    def __init__(self, testsuite: TestSuite, json_schema_path: str = DEFAULT_JSON_SCHEMA_PATH):
        """
        Constructor

        :param testsuite: the TestSuite object
        :type testsuite: TestSuite
        :param json_schema_path: path to the json schema against which the generated `.json`
        report is checked
        :type json_schema_path: str
        """
        self.__testsuite = testsuite
        self.__validator = JsonValidator(json_schema_path)

    def export(self, json_file_path: str):
        """
        This method generates both a test report in `.json` format from the testsuite and a
        `.zip` file containing that report, as well as possible further artifacts added to the
        :class:`TestCase<testguide_report_generator.TestCase.TestCase>` objects.

        :param json_file_path: the path for the output `.json` file
        :type json_file_path: str
        :return: path to the exported `.zip` file
        :rtype: str
        """

        json_repr = self.__testsuite.create_json_repr()

        if self.__validator.validate_json(json_repr):
            with open(json_file_path, 'w', encoding='utf-8') as file:
                file.write(json.dumps(json_repr, indent=4))

            filename = os.path.splitext(json_file_path)[0] if (json_file_path.endswith(".json")) \
                else json_file_path
            zip_file_path = f"{filename}.zip"
            with ZipFile(zip_file_path, 'w') as zip_obj:
                zip_obj.write(json_file_path, os.path.basename(json_file_path), ZIP_DEFLATED)

                for each_testcase in self.__testsuite.get_testcases():
                    self.__add_artifact_to_zip(zip_obj, each_testcase)

            return zip_file_path

        return None

    def __add_artifact_to_zip(self, zip_obj, node):
        """
        Adds the already captured artifact to the upload zip.

        :param zip_obj: Open zipfile object
        :type zip_obj: ZipFile
        :param node: TestCase object or TestCaseFolder object
        :type node: TestCase or TestCaseFolder
        """

        if not isinstance(node, (TestCase, TestCaseFolder)):
            raise TypeError("Argument 'node' must be of type 'TestCase' or 'TestCaseFolder'.")

        if isinstance(node, TestCase):
            for artifact in node.get_artifacts():
                if artifact.get_path_in_upload_zip() not in zip_obj.namelist():
                    zip_obj.write(artifact.get_file_path(), artifact.get_path_in_upload_zip(), ZIP_DEFLATED)
        else:
            # TestCaseFolder
            for testcase in node.get_testcases():
                self.__add_artifact_to_zip(zip_obj, testcase)
