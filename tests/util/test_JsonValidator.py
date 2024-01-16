# Copyright (c) 2023-2024 tracetronic GmbH
#
# SPDX-License-Identifier: MIT

from testguide_report_generator.util.JsonValidator import JsonValidator


def test_json_file_valid(json_schema_path, path_to_valid_json):
    validator = JsonValidator(json_schema_path)
    assert validator.validate_file(path_to_valid_json)


def test_json_file_invalid(json_schema_path, path_to_invalid_json):
    validator = JsonValidator(json_schema_path)
    assert not validator.validate_file(path_to_invalid_json)


def test_default_json_file_valid(path_to_valid_json):
    validator = JsonValidator()
    assert validator.validate_file(path_to_valid_json)


def test_testsuite_valid(json_schema_path, testsuite_json_obj):
    validator = JsonValidator(json_schema_path)
    assert validator.validate_json(testsuite_json_obj)


def test_testsuite_invalid(json_schema_path, testsuite_json_obj):
    testsuite_json_obj["testcases"][1]["testcases"] = []  # empty TestCaseFolder

    validator = JsonValidator(json_schema_path)
    assert not validator.validate_json(testsuite_json_obj)


def test_default_valid(testsuite_json_obj):
    validator = JsonValidator()
    assert validator.validate_json(testsuite_json_obj)
