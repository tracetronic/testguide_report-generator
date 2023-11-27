# Copyright (c) 2023 TraceTronic GmbH
#
# SPDX-License-Identifier: MIT

import pytest

from testguide_report_generator.util.ValidityChecks import gen_error_msg, check_name_length, validate_new_teststep, \
    validate_testcase
from testguide_report_generator.model.TestCase import TestCase, TestStep, TestStepFolder
from testguide_report_generator.model.TestCaseFolder import TestCaseFolder


@pytest.mark.parametrize("name", ["a", "x" * 120])
def test_check_name_length(name):
    assert name == check_name_length(name, "")


@pytest.mark.parametrize("name", ["", "x" * 121])
def test_check_name_length_error(name):
    error_msg = "bad name"
    with pytest.raises(ValueError) as e:
        check_name_length(name, error_msg)

    assert str(e.value) == error_msg


def test_error_msg():
    obj_type = "Type"
    name = "Fred"

    assert "The name of the Type must have a length between 1-120 characters. Name was: Fred" == \
           gen_error_msg(obj_type, name)


def test_teststep_checks(teststep_folder):
    assert validate_new_teststep(teststep_folder, TestStep, TestStepFolder)


def test_teststep_checks_wrong_type():
    with pytest.raises(ValueError) as e:
        validate_new_teststep("", TestStep, TestStepFolder)

    assert str(e.value) == "Argument teststep must be of type TestStep or TestStepFolder."


def test_teststep_checks_empty_error(teststep_folder_empty):
    with pytest.raises(ValueError) as e:
        validate_new_teststep(teststep_folder_empty, TestStep, TestStepFolder)

    assert str(e.value) == "TestStepFolder may not be empty."


def test_testcase_checks(testcase_folder):
    assert validate_testcase(testcase_folder, TestCase, TestCaseFolder)


def test_testcase_checks_wrong_type():
    with pytest.raises(ValueError) as e:
        validate_testcase("", TestCase, TestCaseFolder)

    assert str(e.value) == "Argument testcase must be of type TestCase or TestCaseFolder."


def test_testcase_checks_empty_error(testcase_folder_empty):
    with pytest.raises(ValueError) as e:
        validate_testcase(testcase_folder_empty, TestCase, TestCaseFolder)

    assert str(e.value) == "TestCaseFolder may not be empty."
