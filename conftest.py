# Copyright (c) 2023-2024 tracetronic GmbH
#
# SPDX-License-Identifier: MIT

import json
import os
from unittest.mock import patch

import pytest

from testguide_report_generator.model.TestCase import (
    TestStep,
    Verdict,
    TestStepFolder,
    Parameter,
    Direction,
    Artifact,
    Constant,
    Attribute,
    Review,
    TestCase,
    TestStepArtifact,
    TestStepArtifactType
)
from testguide_report_generator.model.TestCaseFolder import TestCaseFolder
from testguide_report_generator.model.TestSuite import TestSuite

ARTIFACT_PATH = "tests/resources/artifact.txt"
ARTIFACT_PATH_2 = "tests/resources/artifact2.txt"
TESTCASE_JSON_PATH = "tests/resources/testcase.json"
TESTSUITE_JSON_PATH = "tests/resources/testsuite.json"
JSON_SCHEMA_PATH = "testguide_report_generator/schema/schema.json"

PATH_TO_VALID_JSON = "tests/resources/valid.json"
PATH_TO_INVALID_JSON = "tests/resources/invalid.json"


@pytest.fixture
def artifact_path():
    return ARTIFACT_PATH


@pytest.fixture
def artifact_path2():
    return ARTIFACT_PATH_2


@pytest.fixture
def testcase_json_path():
    return TESTCASE_JSON_PATH


@pytest.fixture
def testsuite_json_path():
    return TESTSUITE_JSON_PATH


@pytest.fixture
def json_schema_path():
    return JSON_SCHEMA_PATH


@pytest.fixture
def path_to_valid_json():
    return PATH_TO_VALID_JSON


@pytest.fixture
def path_to_invalid_json():
    return PATH_TO_INVALID_JSON


@pytest.fixture()
def artifact():
    return Artifact(ARTIFACT_PATH)


@pytest.fixture
@patch("testguide_report_generator.model.TestCase.get_md5_hash_from_file")
def artifact_mock_hash(mock_hash):
    mock_hash.return_value = "hash"
    return Artifact(ARTIFACT_PATH)


@pytest.fixture
@patch("testguide_report_generator.model.TestCase.get_md5_hash_from_file")
def teststep_artifact_mock_hash(mock_hash):
    mock_hash.return_value = "hash"
    return TestStepArtifact(ARTIFACT_PATH, TestStepArtifactType.IMAGE)


@pytest.fixture
def teststep():
    return TestStep("ts", Verdict.NONE, "undefined")


@pytest.fixture
def teststep_2():
    teststep_with_desc = TestStep("ts2", Verdict.ERROR, "err").set_description("teststep2")
    return teststep_with_desc


@pytest.fixture
def teststep_folder_empty():
    return TestStepFolder("tsf")


@pytest.fixture
def teststep_folder(teststep, teststep_2):
    tsf = TestStepFolder("tsf")
    tsf.add_teststep(teststep)
    tsf.add_teststep(teststep_2)
    return tsf


@pytest.fixture
def parameter():
    return Parameter("param", 10, Direction.OUT)


@pytest.fixture
def parameter_2():
    return Parameter("param2", 15, Direction.INOUT)


@pytest.fixture
def constant():
    return Constant("const", "one")


@pytest.fixture
def constant_2():
    return Constant("another", "const")


@pytest.fixture
def attribute():
    return Attribute("an", "attribute")


@pytest.fixture
def review():
    return Review("comment", "chucknorris", 1670254005)


@pytest.fixture
def testcase(
        artifact_mock_hash,
        teststep,
        teststep_2,
        teststep_folder,
        parameter,
        parameter_2,
        constant,
        constant_2,
        attribute,
        review,
):
    testcase = TestCase("testcase_one", 1670248341000, Verdict.PASSED)

    testcase.set_description("First testcase.")
    testcase.set_execution_time_in_sec(5)
    testcase.add_parameter_set("myset", [parameter, parameter_2])
    testcase.add_constants([constant, constant_2])
    testcase.add_constant(Constant("", ""))
    testcase.add_constant_pair("const_key", "const_val")
    testcase.add_attribute_pair("an", "attribute")
    testcase.add_setup_teststep(teststep)
    testcase.add_setup_teststep(teststep_folder)
    testcase.add_teardown_teststep(teststep_folder)
    testcase.add_teardown_teststep(teststep_2)
    testcase.add_execution_teststep(teststep_2)
    testcase.add_execution_teststep(teststep_folder)
    testcase.add_artifact(ARTIFACT_PATH, ignore_on_error=False)
    testcase.set_review(review)

    with open("local.json", "w") as file:
        file.write(json.dumps(testcase.create_json_repr()))

    return testcase


@pytest.fixture
def testcase_folder_empty():
    return TestCaseFolder("mytcf")


@pytest.fixture
def testcase_folder(testcase):
    tcf = TestCaseFolder("mytcf2")
    tcf.add_testcase(testcase)

    return tcf


@pytest.fixture
def testsuite():
    return TestSuite("MyTestSuite", 1666698047000)


@pytest.fixture
def testsuite_json_obj():
    testsuite = TestSuite("MyTestSuite", 1666698047000)

    testcase = TestCase("TestCase_1", 1666698047001, Verdict.PASSED)

    testcase.add_parameter_set(
        "MyParameterSet", [Parameter("Input", 7, Direction.IN), Parameter("Output", 42, Direction.OUT)]
    )

    testcase.add_constant_pair("SOP", "2042")

    testcase.add_attribute_pair("ReqId", "007")
    testcase.add_attribute_pair("Designer", "Philipp")

    testcase.add_execution_teststep(TestStep("Check Picture1", Verdict.PASSED, "Shows traffic light"))
    testcase.add_execution_teststep(
        TestStepFolder("Action").add_teststep(TestStep("Check car speed", Verdict.PASSED, "ego >= 120"))
    )
    testcase.add_execution_teststep(TestStep("Check Picture2", Verdict.PASSED, "Shows Ego Vehicle"))

    testcase.add_artifact("testguide_report_generator/schema/schema.json", False)

    testcase.set_review(Review("Review-Comment", "Reviewer", 1423576765001))

    # testcase no. 1: TestCase
    testsuite.add_testcase(testcase)

    testcase_folder = TestCaseFolder("SubFolder")
    testcase_folder.add_testcase(TestCase("TestCase_FAILED", 1423536765000, Verdict.FAILED))

    # testcase no. 2: TestCaseFolder
    testsuite.add_testcase(testcase_folder)

    return testsuite.create_json_repr()


@pytest.fixture(scope="session", autouse=True)
def value_storage():
    return ValueStorage()


class ValueStorage:
    def __init__(self) -> None:
        self.e2e_atxid: str | None = None
        self.remote_testcases_json = None
        self.BASE_URL = os.getenv("TEST_GUIDE_URL")
        self.AUTHKEY = os.getenv("TEST_GUIDE_AUTHKEY")
        self.PROJECT_ID = os.getenv("TEST_GUIDE_PROJECT_ID")
