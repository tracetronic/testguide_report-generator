# Copyright (c) 2023-2024 tracetronic GmbH
#
# SPDX-License-Identifier: MIT

# -*- coding: utf-8 -*-

"""
This module contains the TestSuite class.
"""

from typing import Union

from testguide_report_generator.model.TestCase import TestCase
from testguide_report_generator.model.TestCaseFolder import TestCaseFolder
from testguide_report_generator.util.Json2AtxRepr import Json2AtxRepr
from testguide_report_generator.util.ValidityChecks import check_string_length, validate_testcase


class TestSuite(Json2AtxRepr):
    """
    ATX-TestSuite. This is the top-level element from which the `.json` report will be generated. A
    testsuite must contain at least one :class:`TestCase<testguide_report_generator.TestCase.TestCase>` or
    :class:`TestCaseFolder<testguide_report_generator.TestCaseFolder.TestCaseFolder>` to be test.guide compliant
    """

    __test__ = False  # pytest ignore

    def __init__(self, name: str, timestamp: int):
        """
        Constructor

        :param name: name of the TestSuite
        :type name: str
        :param timestamp: timestamp in milliseconds
        :type timestamp: int
        """
        self.__name = check_string_length(name, 1, 120, "TestSuite", "name")
        self.__timestamp = timestamp
        self.__testcases: list[Union[TestCase, TestCaseFolder]] = []

    def add_testcase(self, testcase: Union[TestCase, TestCaseFolder]):
        """
        Adds a TestCase or TestCaseFolder to the TestSuite.

        :param testcase: testcase to be added
        :type testcase: TestCase or TestCaseFolder
        :raises: ValueError, if the argument is not a TestCase or TestCaseFolder, or if an empty
            TestCaseFolder was added
        :return: this object
        :rtype: TestSuite
        """
        if validate_testcase(testcase, TestCase, TestCaseFolder):
            self.__testcases.append(testcase)
        return self

    def get_testcases(self) -> list:
        """
        :return: Testcases or TestCaseFolders
        :rtype: list
        """
        return self.__testcases

    def create_json_repr(self) -> dict:
        """
        @see: :class:`Json2AtxRepr<testguide_report_generator.Json2AtxRepr>`
        """
        result = {
            'name': self.__name,
            'timestamp': self.__timestamp,
            'testcases':  [each.create_json_repr() for each in self.__testcases]
            }
        return result
