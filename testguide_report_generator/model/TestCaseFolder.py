# Copyright (c) 2023-2024 tracetronic GmbH
#
# SPDX-License-Identifier: MIT

# -*- coding: utf-8 -*-

"""
This module contains the TestCaseFolder class.
"""

from typing import Self
from testguide_report_generator.model.TestCase import TestCase
from testguide_report_generator.util.Json2AtxRepr import Json2AtxRepr
from testguide_report_generator.util.ValidityChecks import check_name_length, gen_error_msg, \
    validate_testcase


class TestCaseFolder(Json2AtxRepr):
    """
    ATX-TestCaseFolder to be added to a :class:`TestSuite<testguide_report_generator.TestSuite.TestSuite>`.
    Each TestSuite must contain at least one TestCase or TestCaseFolder to be test.guide
    compliant. Each TestCaseFolder must contain at least one
    :class:`TestCase<testguide_report_generator.TestCase.TestCase>` to be test.guide compliant.
    """

    __test__ = False  # pytest ignore

    def __init__(self, name: str):
        """
        Constructor

        :param name: name of the testcase folder
        :type name: str
        """
        self.__name = check_name_length(name, gen_error_msg("TestCaseFolder", name))
        self.__testcases: list[TestCase | TestCaseFolder] = []

    def add_testcase(self, testcase: TestCase | Self) -> Self:
        # pylint: disable=R0801
        """
        Adds a TestCase or TestCaseFolder to the testcase folder.

        :param testcase: testcase to be added
        :type testcase: TestCase or TestCaseFolder
        :raises: ValueError, if the argument is not a TestCase or TestCaseFolder
        :return: this object
        :rtype: TestCaseFolder
        """
        if validate_testcase(testcase, TestCase, TestCaseFolder):
            self.__testcases.append(testcase)
        return self

    def get_testcases(self):
        """
        :return: Testcases or TestCaseFolders
        :rtype: list
        """
        return self.__testcases

    def create_json_repr(self):
        """
        :see: :class:`Json2AtxRepr<testguide_report_generator.Json2AtxRepr>`
        """
        result = {
            '@type': "testcasefolder",
            'name': self.__name,
            "testcases": [each.create_json_repr() for each in self.__testcases],
            }
        return result
