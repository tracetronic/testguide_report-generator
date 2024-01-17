# Copyright (c) 2023-2024 tracetronic GmbH
#
# SPDX-License-Identifier: MIT

from zipfile import ZipFile
from unittest.mock import patch

import pytest

from testguide_report_generator.util.File import get_md5_hash_from_file
from testguide_report_generator.util.JsonValidator import JsonValidator
from testguide_report_generator.ReportGenerator import Generator
import os

from testguide_report_generator.model.TestCase import TestCase, Verdict
from testguide_report_generator.model.TestCaseFolder import TestCaseFolder
from testguide_report_generator.model.TestSuite import TestSuite


def test_ReportGenerator_export(testsuite, json_schema_path, artifact_path, artifact_path2):
    pwd = os.getcwd()

    outfile_json_path = pwd + "/export.json"

    testcase = TestCase("name", 123, Verdict.PASSED)
    testcase.add_artifact(artifact_path, ignore_on_error=False)

    testcase_2 = TestCase("name", 123, Verdict.PASSED)
    testcase_2.add_artifact(artifact_path2, ignore_on_error=False)
    testcase_folder = TestCaseFolder("folder")
    testcase_folder.add_testcase(testcase_2)

    testsuite.add_testcase(testcase)
    testsuite.add_testcase(testcase_folder)

    generator = Generator(testsuite, json_schema_path)
    outfile_path = generator.export(outfile_json_path)

    # assert existence of files
    assert pwd + "/export.zip" == outfile_path
    assert os.path.exists(pwd + "/export.json")
    assert os.path.exists(pwd + "/export.zip")

    zip = ZipFile(pwd + "/export.zip")
    zip_contents = zip.namelist()
    artifact_hash = get_md5_hash_from_file(artifact_path)
    artifact_2_hash = get_md5_hash_from_file(artifact_path2)

    # assert content of .zip
    expected_zip_contents = ["export.json", f"{artifact_hash}/artifact.txt", f"{artifact_2_hash}/artifact2.txt"]
    assert all([file in zip_contents for file in expected_zip_contents])

    # assert validity of generated json
    validator = JsonValidator()
    assert validator.validate_file(expected_zip_contents[0])


def test_ReportGenerator_export_invalid_json(testsuite, json_schema_path):
    generator = Generator(testsuite, json_schema_path)
    assert None is generator.export("out.json")


def test_ReportGenerator_export_wrong_testcase_format(json_schema_path):
    with patch.object(TestSuite, "get_testcases") as mock_get_testcases:
        mock_get_testcases.return_value = [""]

        testsuite = TestSuite("test", 1666698047000)
        testcase = TestCase("name", 123, Verdict.PASSED)
        testsuite.add_testcase(testcase)

        generator = Generator(testsuite, json_schema_path)
        with pytest.raises(TypeError):
            generator.export("out.json")
