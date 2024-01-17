# Copyright (c) 2023-2024 tracetronic GmbH
#
# SPDX-License-Identifier: MIT

# -*- coding: utf-8 -*-

"""
Module containing checking methods to ensure that the objects contained in the testsuite, and the
testsuite, are constructed in a valid manner. This guarantees that errors are found early during
setup of the testsuite.
"""


def check_name_length(name, error_msg):
    """
    Checks whether the given name complies to length restrictions according to the schema.

    :param name: name
    :type name: str
    :param error_msg: the error message pertaining to the error thrown, if 'name' is invalid
    :type error_msg: str
    :raises: ValueError, if 'name' length is invalid
    :return: name, if check was successful
    :rtype: str
    """

    if len(name) not in range(1, 121):
        raise ValueError(error_msg)

    return name


def gen_error_msg(obj_type, name):
    """
    Dynamic error message.

    :param obj_type: type of object to which this error message belongs to.
    :type obj_type: str
    :param name: name parameter of the object
    :type name: str
    :return: error message
    :rtype: str
    """
    return f"The name of the {obj_type} must have a length between 1-120 characters. Name was: {name}"


def validate_new_teststep(teststep, stepclass, folderclass):
    """
    Checks whether the TestStep(Folder) object may be added to the TestCase.

    :param teststep: the teststep to be checked
    :type teststep: :class:`TestStep<testguide_report_generator.model.TestCase.TestStep>` or
        :class:`TestStepFolder<testguide_report_generator.model.TestCase.TestStepFolder>`
    :param stepclass: TestStep class
    :type stepclass: :class:`TestStep<testguide_report_generator.model.TestCase.TestStep>`
    :param folderclass: TestStepFolder class
    :type folderclass: :class:`TestStepFolder<testguide_report_generator.model.TestCase.TestStepFolder>`
    :raises: ValueError, if teststep is not a TestStep or TestStepFolder, or if an empty
        TestStepFolder was added
    :return: True, if checks are successful
    :rtype: bool
    """

    if not isinstance(teststep, (stepclass, folderclass)):
        raise ValueError("Argument teststep must be of type TestStep or TestStepFolder.")

    if isinstance(teststep, folderclass):
        if not teststep.get_teststeps():
            raise ValueError("TestStepFolder may not be empty.")

    return True


def validate_testcase(testcase, test_case_class, test_case_folder_class):
    """
    Checks whether the TestCase(Folder) object may be added to the TestSuite.

    :param testcase: the testcase to be checked
    :type testcase: :class:`TestCase<testguide_report_generator.model.TestCase.TestCase>` or
        :class:`TestCaseFolder<testguide_report_generator.model.TestCase.TestCaseFolder>`
    :param test_case_class: TestCase class
    :type test_case_class: :class:`TestCase<testguide_report_generator.model.TestCase.TestCase>`
    :param test_case_folder_class: TestCaseFolder class
    :type test_case_folder_class:
        :class:`TestCaseFolder<testguide_report_generator.model.TestCase.TestCaseFolder>`
    :raises: ValueError, if the argument is not a TestCase or TestCaseFolder, or if an empty
        TestCaseFolder was added
    :return: True, if checks are successful
    :rtype: bool
    """

    if not isinstance(testcase, (test_case_class, test_case_folder_class)):
        raise ValueError("Argument testcase must be of type TestCase or TestCaseFolder.")

    if isinstance(testcase, test_case_folder_class):
        if not testcase.get_testcases():
            raise ValueError("TestCaseFolder may not be empty.")

    return True
