# Copyright (c) 2023 TraceTronic GmbH
#
# SPDX-License-Identifier: MIT
import pytest

from testguide_report_generator.model.TestCase import TestCase, Verdict
from testguide_report_generator.model.TestSuite import TestSuite
import json

NAME_ERROR_MSG = "The name of the TestSuite must have a length between 1-120 characters."


def test_empty(testsuite):
    ts = testsuite
    json_str = json.dumps(ts.create_json_repr())

    assert '{"name": "MyTestSuite", "timestamp": 1666698047000, "testcases": []}' == json_str


def test_add_testcases(testsuite, testcase_folder, testcase):
    ts = testsuite
    ts.add_testcase(testcase)
    ts.add_testcase(testcase_folder)

    assert len(ts.get_testcases()) == 2
    assert len(ts.get_testcases()[1].get_testcases()) == 1


def test_add_testcase_error(testsuite):
    with pytest.raises(ValueError) as error:
        testsuite.add_testcase("")

    assert str(error.value) == "Argument testcase must be of type TestCase or TestCaseFolder."


@pytest.mark.parametrize("input_name", ["", "x" * 121])
def test_value_error(input_name):
    with pytest.raises(ValueError) as e:
        TestSuite(input_name, 0)

    assert str(e.value) == NAME_ERROR_MSG


@pytest.mark.parametrize("input_name", ["a", "x" * 120])
def test_name_valid(input_name):
    json_repr = TestSuite(input_name, 0).create_json_repr()

    assert json_repr["name"] == input_name


def test_correct_json_representation_it(testcase_folder_empty, testcase_folder, testsuite):
    testcase = TestCase("TestCase_1", 1666698047001, Verdict.PASSED)

    testcase_folder_empty.add_testcase(TestCase("name", 0, Verdict.PASSED))
    testsuite.add_testcase(testcase)
    testsuite.add_testcase(testcase_folder_empty)
    testsuite.add_testcase(testcase_folder)

    json_str = json.dumps(testsuite.create_json_repr())

    with open("tests/resources/testsuite.json", "r") as file:
        expected_json_repr = json.load(file)

    assert json.dumps(expected_json_repr) == json_str
