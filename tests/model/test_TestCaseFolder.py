# Copyright (c) 2023 TraceTronic GmbH
#
# SPDX-License-Identifier: MIT

import json

import pytest

from testguide_report_generator.model.TestCase import TestCase, Verdict


def test_empty(testcase_folder_empty):
    tcf = testcase_folder_empty
    json_str = json.dumps(tcf.create_json_repr())

    assert '{"@type": "testcasefolder", "name": "mytcf", "testcases": []}' == json_str


def test_add_testcase(testcase_folder_empty, testcase_folder):
    tcf = testcase_folder_empty
    tcf2 = testcase_folder

    tcf.add_testcase(TestCase("name", 0, Verdict.NONE))
    tcf.add_testcase(tcf2)

    assert len(tcf.get_testcases()) == 2
    assert len(tcf.get_testcases()[1].get_testcases()) == 1


def test_add_testcase_error(testcase_folder_empty):
    with pytest.raises(ValueError) as error:
        testcase_folder_empty.add_testcase("")

    assert str(error.value) == "Argument testcase must be of type TestCase or TestCaseFolder."


def test_correct_json_repr(testcase_folder, testcase_json_path):
    tcf = testcase_folder
    tcf.add_testcase(TestCase("name", 0, Verdict.ERROR))

    json_repr = tcf.create_json_repr()
    tc_json_str = json.dumps(json_repr["testcases"][0])

    with open(testcase_json_path, "r") as file:
        expected_json_repr = json.load(file)

    assert len(json_repr["testcases"]) == 2
    assert json.dumps(expected_json_repr) == tc_json_str
    assert json_repr["testcases"][1]["verdict"] == "ERROR"
