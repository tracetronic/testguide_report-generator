# Copyright (c) 2023-2024 tracetronic GmbH
#
# SPDX-License-Identifier: MIT

# -*- coding: utf-8 -*-

"""
This module contains the TestCase class and all other classes for the creation of a testcase,
including:
    Artifact
    TestStep
    TestStepArtifact
    TestStepArtifactType
    TestStepFolder
    Parameter
    Direction
    Constant
    Attribute
    Review
    Verdict
"""
import errno
import logging
import os
import re
from enum import Enum
from typing import List, Union
from testguide_report_generator.util.Json2AtxRepr import Json2AtxRepr
from testguide_report_generator.util.File import get_md5_hash_from_file
from testguide_report_generator.util.ValidityChecks import check_string_length, validate_new_teststep


class Verdict(Enum):
    """
    ATX-Verdicts.
    """

    NONE = 1
    PASSED = 2
    INCONCLUSIVE = 3
    FAILED = 4
    ERROR = 5


class TestStepArtifactType(Enum):
    """
    Possible types of artifacts attached to test steps
    """

    __test__ = False  # pytest ignore

    IMAGE = 1


class Artifact(Json2AtxRepr):
    """
    TestCase artifact.
    """

    def __init__(self, file_path: str):
        """
        Constructor

        :param file_path: file path to artifact
        :type file_path: str
        :raises OSError: file_path is not a valid path to a file
        """
        if not os.path.isfile(file_path):
            raise OSError(errno.ENOENT, "File does not exist or path does not point to a file", file_path)

        self.__file_path = file_path
        self.__zip_file_path = self.__create_zip_file_path()

    def __create_zip_file_path(self):
        """
        Determines the path to be created in the upload zip.

        :return: path in upload zip
        :rtype: str
        """
        md5_hash = get_md5_hash_from_file(self.__file_path)
        basename = os.path.basename(self.__file_path)
        return f"{md5_hash}/{basename}"

    def get_file_path(self):
        """
        :return: path to file
        :rtype: str
        """
        return self.__file_path

    def get_path_in_upload_zip(self):
        """
        :return: hash-encoded path in the `.zip` file
        :rtype: str
        """
        return self.__zip_file_path

    def create_json_repr(self):
        """
        :see: :class:`Json2AtxRepr<testguide_report_generator.Json2AtxRepr>`
        """
        result = self.__zip_file_path
        return result


class Direction(Enum):
    """
    Parameter directions.
    """

    IN = 1
    OUT = 2
    INOUT = 3


class Parameter(Json2AtxRepr):
    """
    ATX-Parameter.
    """

    def __init__(self, name: str, value, direction: Direction):
        """
        Constructor

        :param name: parameter name
        :type name: str
        :param value: parameter value
        :type value: str or int
        :param direction: parameter direction
        :type direction: Direction
        """
        self.__name = name
        self.__value = value
        self.__direction = direction

    def create_json_repr(self):
        """
        :see: :class:`Json2AtxRepr<testguide_report_generator.Json2AtxRepr>`
        """
        result = {"name": self.__name, "value": self.__value, "direction": self.__direction.name}
        return result


class Constant(Json2AtxRepr):
    """
    ATX-Constant
    """

    def __init__(self, key: str, value: str):
        """
        Constructor

        :param key: Constant key
        :type key: str
        :param value: Constant value
        :type value: str
        """
        str_pattern = "^[a-zA-Z]([a-zA-Z0-9]|_[a-zA-Z0-9])*_?$"
        pattern = re.compile(str_pattern)
        if not pattern.match(key):
            raise ValueError(f"Constant keys need to be structured following this pattern: {str_pattern}")
        check_string_length(key, 1, 128, "Constant", "key")
        self.__key = key
        self.__value = value

    def create_json_repr(self):
        """
        :see: :class:`Json2AtxRepr<testguide_report_generator.Json2AtxRepr>`
        """
        result = {"key": self.__key, "value": self.__value}
        return result


class Attribute(Json2AtxRepr):
    """
    ATX-Attribute.
    """

    def __init__(self, key: str, value: str):
        """
        Constructor

        :param key: Attribute key
        :type key: str
        :param value: Attribute value
        :type value: str
        """
        str_pattern = "^[-.0-9:A-Z_a-z\u00b7\u00c0-\u00d6\u00d8-\u00f6\u00f8-\u037d\u037f-\u1fff\u200c-\u200d\u203f\u2040\u2070-\u218f\u2c00-\u2fef\u3001-\ud7ff\uf900-\ufdcf\ufdf0-\ufffd]+$"
        pattern = re.compile(str_pattern)
        if not pattern.match(key):
            raise ValueError(f"Attribute keys need to be structured following this pattern: {str_pattern}")
        check_string_length(key, 1, 255, "Attribute", "key")
        self.__key = key
        self.__value = value

    def create_json_repr(self):
        """
        :see: :class:`Json2AtxRepr<testguide_report_generator.Json2AtxRepr>`
        """
        result = {"key": self.__key, "value": self.__value}
        return result


class Review(Json2AtxRepr):
    """
    TestCase review.
    """

    def __init__(self, comment: str, author: str, timestamp: int):
        """Constructor

        :param comment: Review comment (1-10000 characters)
        :type comment: str
        :param author: Review author
        :type author: str
        :param timestamp: UTC timestamp in seconds
        :rtype timestamp: int
        """

        check_string_length(comment, 1, 10000, "Review", "comment")
        check_string_length(author, 0, 512, "Review", "author")

        self.__comment = comment
        self.__author = author
        self.__timestamp = timestamp
        self.__summary: str | None = None
        self.__verdict: Verdict | None = None
        self.__defect: str | None = None
        self.__defect_priority: str | None = None
        self.__tickets: list[str] = []
        self.__invalid_run: bool = False
        self.__custom_evaluation: str | None = None
        self.__tags: list[str] = []
        self.__contacts: list[str] = []

    def set_verdict(self, verdict: Verdict):
        """
        Set the verdict for the review.

        :param verdict: Review verdict
        :type verdict: Verdict
        :return: this object
        :rtype: Review
        """
        if not isinstance(verdict, Verdict):
            raise TypeError("Argument 'verdict' must be of type 'Verdict'.")
        self.__verdict = verdict
        return self

    def set_summary(self, summary: str):
        """
        Set the review summary.

        :param summary: Review summary
        :type summary: str
        :return: this object
        :rtype: Review
        """
        check_string_length(summary, 0, 512, "Review", "summary")
        self.__summary = summary
        return self

    def set_defect(self, defect: str):
        """
        Set the defect information.

        :param defect: Review defect
        :type defect: str
        :return: this object
        :rtype: Review
        """
        check_string_length(defect, 0, 64, "Review", "defect")
        self.__defect = defect
        return self

    def set_defect_priority(self, defect_priority: str):
        """
        Set the defect priority.

        :param defect_priority: Review priority
        :type priority: str
        :return: this object
        :rtype: Review
        """
        check_string_length(defect_priority, 0, 64, "Review", "defectPriority")
        self.__defect_priority = defect_priority
        return self

    def add_tickets(self, tickets: List[str]):
        """
        Add tickets to the review.

        :param tickets: list of Review tickets
        :type tickets: list
        :return: this object
        :rtype: Review
        """
        for ticket in tickets:
            check_string_length(ticket, 0, 512, "Review", "ticket")
        self.__tickets.extend(tickets)
        return self

    def set_invalid_run(self, invalid: bool):
        """
        Mark the review as an invalid run.

        :param invalid: Review invalid
        :type invalid: bool
        :return: this object
        :rtype: Review
        """
        self.__invalid_run = invalid
        return self

    def set_custom_evaluation(self, custom_evaluation: str):
        """
        Set a custom evaluation message.

        :param custom_evaluation: Review evaluation
        :type custom_evaluation: str
        :return: this object
        :rtype: Review
        """
        check_string_length(custom_evaluation, 0, 64, "Review", "customEvaluation")
        self.__custom_evaluation = custom_evaluation
        return self

    def add_tags(self, tags: List[str]):
        """
        Add multiple tags to the review.

        :param tags: list of Review tags
        :type tags: list
        :return: this object
        :rtype: Review
        """
        self.__tags.extend(tags)
        return self

    def add_contacts(self, contacts: List[str]):
        """Add  contacts to the review.

        :param contacts: list of Review contacts
        :type contacts: list
        :return: this object
        :rtype: Review
        """
        for contact in contacts:
            check_string_length(contact, 0, 255, "Review", "contact")
        self.__contacts.extend(contacts)
        return self

    def create_json_repr(self):
        """
        :see: :class:`Json2AtxRepr<testguide_report_generator.Json2AtxRepr>`
        """
        result = {
            "comment": self.__comment,
            "timestamp": self.__timestamp,
            "verdict": self.__verdict,
            "author": self.__author,
            "summary": self.__summary,
            "defect": self.__defect,
            "defectPriority": self.__defect_priority,
            "tickets": self.__tickets,
            "invalidRun": self.__invalid_run,
            "customEvaluation": self.__custom_evaluation,
            "tags": self.__tags,
            "contacts": self.__contacts,
        }
        if self.__verdict:
            result["verdict"] = self.__verdict.name
        else:
            result["verdict"] = "PASSED"
        return result


class TestStepArtifact(Artifact):
    """
    Artifact attached to an ATX-TestStep
    """

    __test__ = False  # pytest ignore

    def __init__(self, file_path: str, artifact_type: TestStepArtifactType):
        """
        Constructor

        :param file_path: file path to the artifact
        :type file_path: str
        :param artifact_type: Type of the artifact (currently only images are supported)
        :type artifact_type: TestStepArtifactType
        :raises TypeError: artifact_type is not of type TestStepArtifactType
        :raises OSError: file_path is not a valid path to a file
        """
        super().__init__(file_path)

        if not isinstance(artifact_type, TestStepArtifactType):
            raise TypeError("Argument 'artifact_type' must be of type 'TestStepArtifactType'.")

        self.__artifact_type = artifact_type

    def get_artifact_type(self):
        """
        returns the artifacts type

        :rtype: TestStepArtifactType
        """
        return self.__artifact_type

    def create_json_repr(self):
        """
        :see: :class:`Json2AtxRepr<testguide_report_generator.Json2AtxRepr>`
        """
        return {"path": self.get_path_in_upload_zip(), "artifactType": self.__artifact_type.name}


class TestStep(Json2AtxRepr):
    """
    ATX-TestStep.
    """

    __test__ = False  # pytest ignore

    def __init__(self, name: str, verdict: Verdict, expected_result: str = ""):
        """
        Constructor

        :param name: label of the teststep
        :type name: str
        :param verdict: teststep verdict
        :type verdict: Verdict
        :param expected_result: expected result of the teststep
        :type expected_result: str
        :raises TypeError: argument 'verdict' is not of type Verdict
        """
        self.__name = check_string_length(name, 1, 255, "TestStep", "name")

        if not isinstance(verdict, Verdict):
            raise TypeError("Argument 'verdict' must be of type 'Verdict'.")

        self.__description: str | None = None
        self.__verdict = verdict
        self.__expected_result = check_string_length(expected_result, 0, 1024, "TestStep", "expected_result")
        self.__artifacts: list[Artifact] = []

    def set_description(self, desc: str):
        """
        Set the test case description.

        :param desc: teststep description
        :type desc: str
        :return: this object
        :rtype: teststep
        """
        self.__description = desc
        return self

    def add_artifact(self, file_path: str, artifact_type: TestStepArtifactType, ignore_on_error: bool = False):
        """
        Add an artifact to the TestStep. Allows to ignore the artifact, if it does not exist.

        :param file_path: path to artifact
        :type file_path: str
        :param artifact_type: type of the artifact
        :type artifact_type: TestStepArtifactType
        :param ignore_on_error: set to True, to skip this artifact if it does not exist (will not raise an error)
        :type ignore_on_error: bool
        :raises OSError: file_path is invalid, only when ignore_on_error = False
        :raises TypeError: artifact_type is not of type TestStepArtifactType
        :return: this object
        :rtype: TestStep
        """
        try:
            artifact = TestStepArtifact(file_path, artifact_type)
            self.__artifacts.append(artifact)
        except OSError as error:
            if not ignore_on_error:
                raise error
            logging.warning(
                f"Artifact path '{file_path}' for teststep '{self.__name}' is invalid, " f"will be ignored!"
            )
        return self

    def get_artifacts(self):
        """
        Get the TestSteps artifacts

        :return: list of TestStepArtifact
        :rtype: list
        """
        return self.__artifacts

    def create_json_repr(self):
        """
        :see: :class:`Json2AtxRepr<testguide_report_generator.Json2AtxRepr>`
        """
        result = {
            "@type": "teststep",
            "name": self.__name,
            "description": self.__description,
            "verdict": self.__verdict.name,
            "expected_result": self.__expected_result,
            "testStepArtifacts": [each.create_json_repr() for each in self.__artifacts],
        }
        return result


class TestStepFolder(Json2AtxRepr):
    """
    ATX-TestStepFolder. Each teststep folder must contain at least one TestStep to be test.guide
    compliant.
    """

    __test__ = False  # pytest ignore

    def __init__(self, name: str):
        """
        Constructor

        :param name: TestStepFolder name
        :type name: str
        """
        self.__name = check_string_length(name, 1, 255, "TestStepFolder", "name")
        self.__description: str | None = None
        self.__teststeps: list[Union[TestStep, TestStepFolder]] = []

    def set_description(self, desc: str):
        """
        Set the test case description.

        :param desc: teststep description
        :type desc: str
        :return: this object
        :rtype: teststep
        """
        self.__description = desc
        return self

    def add_teststep(self, teststep):
        """
        Adds a TestStep or TestStepFolder to the teststep folder.

        :param teststep: TestStep to be added
        :type teststep: TestStep or TestStepFolder
        :raises TypeError: the argument is not a TestStep or TestStepFolder
        :return: this object
        :rtype: TestStepFolder
        """
        if not isinstance(teststep, (TestStep, TestStepFolder)):
            raise TypeError("Argument teststep must be of type TestStep or TestStepFolder.")

        self.__teststeps.append(teststep)
        return self

    def get_teststeps(self):
        """
        :return: all teststeps of the TestStepFolder
        :rtype: list
        """
        return self.__teststeps

    def create_json_repr(self):
        """
        :see: :class:`Json2AtxRepr<testguide_report_generator.Json2AtxRepr>`
        """
        result = {
            "@type": "teststepfolder",
            "name": self.__name,
            "description": self.__description,
            "teststeps": [each.create_json_repr() for each in self.__teststeps],
        }
        return result


class TestCase(Json2AtxRepr):
    """
    ATX-TestCase to be added to a :class:`TestSuite<testguide_report_generator.TestSuite.TestSuite>`. Each
    TestSuite must contain at least one testcase to be test.guide compliant (or, alternatively,
    at least one :class:`TestCaseFolder<testguide_report_generator.TestCaseFolder.TestCaseFolder>`).
    """

    __test__ = False  # pytest ignore

    def __init__(self, name: str, timestamp: int, verdict: Verdict):
        """
        Constructor

        :param name: Name of the testcase
        :type name: str
        :param timestamp: timestamp in milliseconds
        :type timestamp: int
        :param verdict: testcase verdict
        :type verdict: Verdict
        :raises: TypeError, if the argument 'verdict' is not of type Verdict
        """

        self.__name = check_string_length(name, 1, 120, "TestCase", "name")
        self.__timestamp = timestamp

        if not isinstance(verdict, Verdict):
            raise TypeError("Argument 'verdict' must be of type 'Verdict'.")
        self.__verdict = verdict

        self.__execution_time = 0
        self.__description: str | None = None

        self.__setup_teststeps: list[Union[TestStep, TestStepFolder]] = []
        self.__execution_teststeps: list[Union[TestStep, TestStepFolder]] = []
        self.__teardown_teststeps: list[Union[TestStep, TestStepFolder]] = []

        self.__param_set: str | None = None
        self.__parameters: list[Parameter] = []

        self.__attributes: list[Attribute] = []
        self.__constants: list[Constant] = []

        self.__artifacts: list[Artifact] = []

        self.__review: Review | None = None

    def set_description(self, desc: str):
        """
        Set the test case description.

        :param desc: testcase description
        :type desc: str
        :return: this object
        :rtype: TestCase
        """
        self.__description = desc
        return self

    def set_execution_time_in_sec(self, exec_time: int):
        """
        Set the execution time of the testcase.

        :param exec_time: execution time in seconds > 0
        :type exec_time: int
        :return: this object
        :rtype: TestCase
        """
        self.__execution_time = exec_time
        return self

    def add_parameter_set(self, param_set: str, params: List[Parameter]):
        """
        Set the parameter set.

        :param param_set: name of the parameter set
        :type param_set: str or None
        :param params: list of Parameter
        :type params: list
        :raises TypeError: the 'params' parameter has the wrong type
        :return: this object
        :rtype: TestCase
        """
        check_string_length(param_set, 0, 1024, "TestCase", "paramSet")
        self.__param_set = param_set

        if not all(isinstance(param, Parameter) for param in params):
            raise TypeError("Argument params must be of type list from Parameter.")

        self.__parameters = params
        return self

    def add_constants(self, constants: List[Constant]):
        """
        Add a list of constants to the test case.

        :param constants: list of Constant
        :type constants: list
        :raises TypeError: constants contains at least one element which has the wrong type
        :return: this object
        :rtype: TestCase
        """

        if not all(isinstance(constant, Constant) for constant in constants):
            raise TypeError("Argument constants must be of type list from Constant.")

        for each in constants:
            self.add_constant(each)

        return self

    def add_constant(self, constant: Constant):
        """
        Add a constant to the test case.

        :param constant: ATX-Constant
        :type constant: Constant
        :raises TypeError: the argument is of the wrong type
        :return: this object
        :rtype: TestCase
        """

        if not isinstance(constant, Constant):
            raise TypeError("Argument constant must be of type Constant.")
        self.__constants.append(constant)
        return self

    def add_constant_pair(self, key: str, value: str):
        """
        Add a constant to the testcase.

        :param key: Constant key
        :type key: str
        :param value: Constant value
        :type value: str
        :return: this object
        :rtype: TestCase
        """
        self.add_constant(Constant(key, value))
        return self

    def add_attribute_pair(self, key: str, value: str):
        """
        Add an attribute to the testcase.

        :param key: Attribute key
        :type key: str
        :param value: Attribute value
        :type value: str
        :return: this object
        :rtype: TestCase
        """
        self.__attributes.append(Attribute(key, value))
        return self

    def add_setup_teststep(self, teststep: Union[TestStep, TestStepFolder]):
        """
        Adds a TestStep or TestStepFolder to the setup/precondition teststeps.

        :param teststep: TestStep to be added
        :type teststep: TestStep or TestStepFolder
        :raises: ValueError, if the argument is not a TestStep or TestStepFolder, or if an empty
            TestStepFolder was added
        :return: this object
        :rtype: TestCase
        """
        if validate_new_teststep(teststep, TestStep, TestStepFolder):
            self.__setup_teststeps.append(teststep)
        return self

    def add_execution_teststep(self, teststep: Union[TestStep, TestStepFolder]):
        """
        Adds a TestStep or TestStepFolder to the execution test steps.

        :param teststep: TestStep to be added
        :type teststep: TestStep or TestStepFolder
        :raises: ValueError, if the argument is not a TestStep or TestStepFolder, or if an empty
            TestStepFolder was added
        :return: this object
        :rtype: TestCase
        """
        if validate_new_teststep(teststep, TestStep, TestStepFolder):
            self.__execution_teststeps.append(teststep)
        return self

    def add_teardown_teststep(self, teststep: Union[TestStep, TestStepFolder]):
        """
        Adds a TestStep or TestStepFolder to the teardown/postcondition test steps.

        :param teststep: TestStep to be added
        :type teststep: TestStep or TestStepFolder
        :raises: ValueError, if the argument is not a TestStep or TestStepFolder, or if an empty
            TestStepFolder was added
        :return: this object
        :rtype: TestCase
        """
        if validate_new_teststep(teststep, TestStep, TestStepFolder):
            self.__teardown_teststeps.append(teststep)
        return self

    def add_artifact(self, artifact_file_path: str, ignore_on_error: bool = False):
        """
        Adds an arbitrary artifact to the testcase execution.

        :param artifact_file_path: artifact file path
        :type artifact_file_path: str
        :param ignore_on_error: True, if this file should simply be ignored if the file path is
            accessed incorrectly, otherwise False.
        :type ignore_on_error: bool
        :raises OSError: file_path is invalid, only when ignore_on_error = False
        :return: this object
        :rtype: TestStep
        """
        try:
            artifact = Artifact(artifact_file_path)
            self.__artifacts.append(artifact)
        except OSError as error:
            if not ignore_on_error:
                raise error
            logging.warning(
                f"Artifact path '{artifact_file_path}' for testcase" f" '{self.__name}' is invalid, will be ignored!"
            )
        return self

    def get_artifacts(self):
        """
        :return: Attached files to the testcase and its test steps.
        :rtype: list
        """
        result = []
        result.extend(self.__artifacts)
        for step in self.__setup_teststeps:
            result.extend(self.__collect_teststep_artifacts(step))
        for step in self.__execution_teststeps:
            result.extend(self.__collect_teststep_artifacts(step))
        for step in self.__teardown_teststeps:
            result.extend(self.__collect_teststep_artifacts(step))
        return result

    def set_review(self, review: Review):
        """
        Set a review for the testcase.

        :param review: Review for testcase
        :type review: Review
        :raises TypeError: the argument is of the wrong type
        """
        if not isinstance(review, Review):
            raise TypeError("Argument review must be of type Review.")
        self.__review = review
        return self

    def create_json_repr(self):
        """
        :see: :class:`Json2AtxRepr<testguide_report_generator.Json2AtxRepr>`
        """
        result = {
            "@type": "testcase",
            "name": self.__name,
            "verdict": self.__verdict.name,
            "description": self.__description,
            "timestamp": self.__timestamp,
            "executionTime": self.__execution_time,
            "parameters": [each.create_json_repr() for each in self.__parameters],
            "paramSet": self.__param_set,
            "setupTestSteps": [each.create_json_repr() for each in self.__setup_teststeps],
            "executionTestSteps": [each.create_json_repr() for each in self.__execution_teststeps],
            "teardownTestSteps": [each.create_json_repr() for each in self.__teardown_teststeps],
            "attributes": [each.create_json_repr() for each in self.__attributes],
            "constants": [each.create_json_repr() for each in self.__constants],
            "environments": [],
            "artifacts": [each.create_json_repr() for each in self.__artifacts],
        }
        if self.__review:
            result["review"] = self.__review.create_json_repr()
        return result

    def __collect_teststep_artifacts(self, teststep) -> list:
        """
        Helper method to recursively collect all artifacts in a TestStep/TestStepFolder hierarchy
        """
        result = []
        if isinstance(teststep, TestStep):
            result.extend(teststep.get_artifacts())
        elif isinstance(teststep, TestStepFolder):
            for item in teststep.get_teststeps():
                result.extend(self.__collect_teststep_artifacts(item))
        return result
