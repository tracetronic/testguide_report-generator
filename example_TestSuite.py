# Copyright (c) 2023-2024 tracetronic GmbH
#
# SPDX-License-Identifier: MIT

"""
Example Script.
"""
from testguide_report_generator import TestSuite, TestCase, TestStep, TestStepFolder, Verdict, Parameter, \
    Direction, Review, TestStepArtifactType, TestCaseFolder, Generator


def create_testsuite():
    """
    Creates an example TestSuite and outputs an example .json report file.
    """

    testsuite = TestSuite("MyTestSuite", 1666698047000)

    testcase = TestCase("TestCase_1", 1666698047001, Verdict.PASSED)
    testcase.add_parameter_set("MyParameterSet", [Parameter("Input", 7, Direction.IN),
                                                  Parameter("Output", 42, Direction.OUT)])
    testcase.add_constant_pair("SOP", "2042")
    testcase.add_attribute_pair("ReqId", "007")
    testcase.add_attribute_pair("Designer", "Philipp")
    testcase.add_execution_teststep(TestStep("Check Picture1", Verdict.PASSED,
                                             "Shows traffic light"))
    testcase.add_execution_teststep(TestStepFolder("Action")
                                    .add_teststep(TestStep("Check car speed", Verdict.PASSED,
                                                           "ego >= 120")))
    teststep = TestStep("Check Picture2", Verdict.PASSED, "Shows Ego Vehicle")
    teststep.add_artifact("docs/images/Logo_TEST-GUIDE_rgb_SCREEN.png", TestStepArtifactType.IMAGE)
    testcase.add_execution_teststep(teststep)
    testcase.add_artifact("testguide_report_generator/schema/schema.json", False)

    review = Review("Review-Comment", "Reviewer",1423576765001)

    testcase.set_review(review)
    testsuite.add_testcase(testcase)
    testcase_folder = TestCaseFolder("SubFolder")
    testcase_folder.add_testcase(TestCase("TestCase_FAILED", 1423536765000, Verdict.FAILED))
    testsuite.add_testcase(testcase_folder)

    json_generator = Generator(testsuite)
    json_generator.export("example.json")


if __name__ == "__main__":
    create_testsuite()
