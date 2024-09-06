# Copyright (c) 2023-2024 tracetronic GmbH
#
# SPDX-License-Identifier: MIT

"""
This module provides essential imports for the tests model package.
"""

from testguide_report_generator.model.TestCase import (TestCase, TestStep, Verdict, Artifact, TestStepArtifact,
                                                       TestStepArtifactType)
from testguide_report_generator.model.TestSuite import TestSuite
from testguide_report_generator.util.ValidityChecks import gen_error_msg

__all__ = [
    "TestCase",
    "TestStep",
    "Verdict",
    "Artifact",
    "TestStepArtifact",
    "TestStepArtifactType",
    "TestSuite",
    "gen_error_msg"
]
