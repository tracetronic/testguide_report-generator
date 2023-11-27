# Copyright (c) 2023 TraceTronic GmbH
#
# SPDX-License-Identifier: MIT
from datetime import datetime

from testguide_report_generator.model.TestSuite import TestSuite
from testguide_report_generator.model.TestCase import (
    TestCase,
    TestStep,
    TestStepFolder,
    Verdict,
    Parameter,
    Direction,
    Review,
)
from testguide_report_generator.model.TestCaseFolder import TestCaseFolder
from testguide_report_generator.ReportGenerator import Generator


def create_testsuite():
    timestamp = round(datetime.timestamp(datetime.now())) * 1000
    testsuite = TestSuite("E2E_TG_JSON_GENERATOR", timestamp)

    testcase_passed = TestCase("testcase_passed", timestamp + 1, Verdict.PASSED)
    testcase_passed.set_description("TestCaseDesc")
    testcase_passed.add_parameter_set(
        "MyParameterSet", [Parameter("Input", 7, Direction.IN), Parameter("Output", 42, Direction.OUT)]
    )
    testcase_passed.add_constant_pair("SOP", "2042")
    testcase_passed.add_attribute_pair("ReqId", "007")
    testcase_passed.add_attribute_pair("Designer", "Philipp")
    testcase_passed.add_setup_teststep(TestStep("Check Picture0", Verdict.PASSED, "Shows nothing"))

    teststep_with_desc = TestStep("Check Pic1", Verdict.PASSED, "Shows traffic light").set_description("TestStepDesc")
    testcase_passed.add_execution_teststep(teststep_with_desc)

    testcase_passed.add_execution_teststep(
        TestStepFolder("Action").add_teststep(TestStep("Check car speed", Verdict.PASSED, "ego >= 120"))
    )
    testcase_passed.add_execution_teststep(TestStep("Check Pic2", Verdict.PASSED, "Shows Ego Vehicle"))
    testcase_passed.add_artifact("testguide_report_generator/schema/schema.json", False)
    testcase_passed.set_review(Review("Review-Comment", "Reviewer", timestamp + 2))
    testsuite.add_testcase(testcase_passed)

    testcase_failed = TestCase("testcase_failed", timestamp + 3, Verdict.FAILED)
    testcase_folder = TestCaseFolder("Testcase Folder")
    testcase_folder.add_testcase(testcase_passed)
    testcase_folder.add_testcase(testcase_failed)
    testsuite.add_testcase(testcase_folder)

    testcase_error = TestCase("testcase_error", timestamp, Verdict.ERROR)
    testcase_error.set_description("This testcase is supposed to error")
    testcase_inconclusive = TestCase("testcase_inconclusive", timestamp, Verdict.INCONCLUSIVE)
    testcase_verdict_none = TestCase("testcase_verdict_none", timestamp, Verdict.NONE)
    testcase_folder2 = TestCaseFolder("Testcase Folder 2")
    testcase_folder2.add_testcase(testcase_error)
    testcase_folder2.add_testcase(testcase_inconclusive)
    testcase_folder2.add_testcase(testcase_verdict_none)
    testsuite.add_testcase(testcase_folder2)

    testcase_passed2 = TestCase("testcase_passed2", timestamp + 10, Verdict.PASSED)
    testcase_folder3 = TestCaseFolder("Testcase Folder 3")
    testcase_folder3.add_testcase(testcase_passed2)
    testsuite.add_testcase(testcase_folder3)

    json_generator = Generator(testsuite)
    json_generator.export("e2e.json")
