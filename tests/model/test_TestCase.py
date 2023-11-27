# Copyright (c) 2023 TraceTronic GmbH
#
# SPDX-License-Identifier: MIT

import pytest
import json
from unittest.mock import patch

from testguide_report_generator.model.TestCase import (TestCase, TestStep, Verdict, Artifact, TestStepArtifact,
                                                       TestStepArtifactType)
from testguide_report_generator.util.ValidityChecks import gen_error_msg


class TestArtifact:
    def test_new_artifact(self, artifact_path):
        artifact = Artifact(artifact_path)
        assert artifact.get_file_path() == artifact_path

    def test_new_artifact_error(self):
        with pytest.raises(OSError, match="File does not exist or path does not point to a file"):
            Artifact("does/not/exist.txt")

    def test_correct_json_repr(self, artifact_mock_hash):
        json_str = json.dumps(artifact_mock_hash.create_json_repr())
        assert '"hash/artifact.txt"' == json_str


class TestTestStepArtifact:
    def test_new(self, artifact_path):
        artifact = TestStepArtifact(artifact_path, TestStepArtifactType.IMAGE)
        assert artifact.get_file_path() == artifact_path
        assert artifact.get_artifact_type() == TestStepArtifactType.IMAGE

    def test_new_error(self, artifact_path):
        with pytest.raises(TypeError, match="TestStepArtifactType"):
            TestStepArtifact(artifact_path, "IMAGE")

    def test_correct_json_repr(self, teststep_artifact_mock_hash):
        json_str = json.dumps(teststep_artifact_mock_hash.create_json_repr())
        assert json_str == '{"path": "hash/artifact.txt", "artifactType": "IMAGE"}'


class TestTestStep:

    @patch("testguide_report_generator.model.TestCase.get_md5_hash_from_file")
    def test_correct_json_repr(self, mock, teststep, artifact_path):
        mock.return_value = "hash"
        teststep.add_artifact(artifact_path, TestStepArtifactType.IMAGE, False)
        assert len(teststep.get_artifacts()) == 1
        json_str = json.dumps(teststep.create_json_repr())

        assert (
                '{"@type": "teststep", "name": "ts", "description": null, '
                '"verdict": "NONE", "expected_result": "undefined", "testStepArtifacts": '
                '[{"path": "hash/artifact.txt", "artifactType": "IMAGE"}]}' == json_str
        )

    def test_invalid_verdict(self):
        with pytest.raises(TypeError) as e:
            TestStep("a", "verdict")

        assert str(e.value) == "Argument 'verdict' must be of type 'Verdict'."

    def test_add_artifact_oserror(self, teststep, caplog):
        with pytest.raises(OSError, match="File does not exist or path does not point to a file"):
            teststep.add_artifact("invalid/path.obj", TestStepArtifactType.IMAGE, False)

        teststep.add_artifact("invalid/path.obj", TestStepArtifactType.IMAGE, True)
        assert "Artifact path 'invalid/path.obj' for teststep 'ts' is invalid, will be ignored!" in caplog.text

    def test_add_artifact_typeerror(self, teststep, artifact_path):
        with pytest.raises(TypeError, match="TestStepArtifactType"):
            teststep.add_artifact(artifact_path, "invalid", True)


class TestTestStepFolder:
    def test_correct_json_repr(self, teststep_folder):
        tsf = teststep_folder.set_description("abc")
        json_str = json.dumps(tsf.create_json_repr())

        assert (
                '{"@type": "teststepfolder", "name": "tsf", "description": "abc", '
                '"teststeps": ['
                '{"@type": "teststep", "name": "ts", "description": null, "verdict": "NONE", "expected_result": '
                '"undefined", "testStepArtifacts": []},'
                ' {"@type": "teststep", "name": "ts2", "description": "teststep2", "verdict": "ERROR",'
                ' "expected_result": "err", "testStepArtifacts": []}]}' == json_str
        )

    def test_add_teststep_error(self, teststep_folder):
        with pytest.raises(TypeError) as error:
            teststep_folder.add_teststep("")

        assert str(error.value) == "Argument teststep must be of type TestStep or TestStepFolder."


class TestParameter:
    def test_correct_json_repr(self, parameter):
        json_str = json.dumps(parameter.create_json_repr())
        assert '{"name": "param", "value": 10, "direction": "OUT"}' == json_str


class TestTestCase:
    def test_add_parameter_error(self, testcase):
        with pytest.raises(TypeError) as error:
            testcase.add_parameter_set("", [""])

        assert str(error.value) == "Argument params must be of type list from Parameter."

    def test_add_constants_error(self, testcase):
        with pytest.raises(TypeError) as error:
            testcase.add_constants([""])

        assert str(error.value) == "Argument constants must be of type list from Constant."

    def test_add_constant_error(self, testcase):
        with pytest.raises(TypeError) as error:
            testcase.add_constant("")

        assert str(error.value) == "Argument constant must be of type Constant."

    def test_set_review_error(self, testcase):
        with pytest.raises(TypeError) as error:
            testcase.set_review("")

        assert str(error.value) == "Argument review must be of type Review."

    @pytest.mark.parametrize("input_name", ["a", "x" * 120])
    def test_default(self, input_name):
        verdict = Verdict.FAILED
        tc = TestCase(input_name, 0, verdict)
        json_repr = tc.create_json_repr()

        assert json_repr["name"] == input_name
        assert json_repr["timestamp"] == 0
        assert json_repr["verdict"] == "FAILED"

    @pytest.mark.parametrize("input_name", ["", "x" * 121])
    def test_value_error(self, input_name):
        verdict = Verdict.FAILED
        with pytest.raises(ValueError) as e:
            TestCase(input_name, 0, verdict)

        assert str(e.value) == gen_error_msg("TestCase", input_name)

    def test_invalid_verdict(self):
        with pytest.raises(TypeError) as e:
            TestCase("a", 0, "verdict")

        assert str(e.value) == "Argument 'verdict' must be of type 'Verdict'."

    def test_add_artifact(self, artifact_path):
        tc = TestCase("name", "", Verdict.PASSED)

        with pytest.raises(OSError) as error:
            tc.add_artifact("", ignore_on_error=False)

        assert str(error.value) == "[Errno 2] File does not exist or path does not point to a file: ''"

        tc.add_artifact(artifact_path, ignore_on_error=False)
        tc.add_artifact("", ignore_on_error=True)

        assert len(tc.get_artifacts()) == 1

    def test_collect_artifacts(self, teststep_folder, artifact_path):
        ts = TestStep("ts", Verdict.FAILED).add_artifact(artifact_path, TestStepArtifactType.IMAGE)
        tc = TestCase("dummy", 0, Verdict.PASSED)
        tc.add_artifact(artifact_path)
        tc.add_execution_teststep(teststep_folder)
        tc.add_setup_teststep(ts)
        tc.add_teardown_teststep(ts)
        assert len(tc.get_artifacts()) == 3

    def test_correct_json_repr(self, testcase, testcase_json_path):
        json_str = json.dumps(testcase.create_json_repr())

        with open(testcase_json_path, "r") as file:
            expected_json_repr = json.load(file)

        assert json.dumps(expected_json_repr) == json_str

    def test_add_teststeps_error(self, testcase):
        ERROR_MSG = "Argument teststep must be of type TestStep or TestStepFolder."

        with pytest.raises(ValueError) as error:
            testcase.add_setup_teststep("")

        assert str(error.value) == ERROR_MSG

        with pytest.raises(ValueError) as error:
            testcase.add_execution_teststep("")

        assert str(error.value) == ERROR_MSG

        with pytest.raises(ValueError) as error:
            testcase.add_teardown_teststep("")

        assert str(error.value) == ERROR_MSG

    def test_add_empty_teststep_folder_error(self, teststep_folder_empty, testcase):
        ERROR_MSG = "TestStepFolder may not be empty."

        with pytest.raises(ValueError) as error:
            testcase.add_teardown_teststep(teststep_folder_empty)

        assert str(error.value) == ERROR_MSG

        with pytest.raises(ValueError) as error:
            testcase.add_execution_teststep(teststep_folder_empty)

        assert str(error.value) == ERROR_MSG

        with pytest.raises(ValueError) as error:
            testcase.add_setup_teststep(teststep_folder_empty)

        assert str(error.value) == ERROR_MSG


class TestConstant:
    def test_correct_json_repr(self, constant):
        json_str = json.dumps(constant.create_json_repr())
        assert '{"key": "const", "value": "one"}' == json_str


class TestAttribute:
    def test_correct_json_repr(self, attribute):
        json_str = json.dumps(attribute.create_json_repr())
        assert '{"key": "an", "value": "attribute"}' == json_str


class TestReview:
    def test_correct_json_repr(self, review):
        json_str = json.dumps(review.create_json_repr())
        assert '{"comment": "comment", "timestamp": 1670254005, "author": "chucknorris"}' == json_str
