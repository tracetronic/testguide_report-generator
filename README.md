<!--
Copyright (c) 2022-2024 tracetronic GmbH

SPDX-License-Identifier: MIT
-->

# test.guide Report Generator


[![Test](https://github.com/tracetronic/testguide_report-generator/actions/workflows/test.yml/badge.svg)](https://github.com/tracetronic/testguide_report-generator/actions/workflows/test.yml) [![Releases](https://img.shields.io/badge/Releases-Changelog-blue)](https://github.com/tracetronic/testguide_report-generator/releases) [![License](https://img.shields.io/badge/license-MIT-blue.svg?style=flat)](https://github.com/tracetronic/testguide_report-generator/blob/main/LICENSE) 

As a modern automotive test engineer, reliance on automated solutions for the execution, reporting and evaluation of my test suites is essential.
The complexity of the systems under test, and thus the amount of necessary tests is ever growing tremendously. One of the tools which can help
with these tasks is [tracetronic test.guide](https://www.tracetronic.com/products/test-guide/). As a user of test.guide, it is desirable to have
a means to customize and structure my test reports in a simple manner. 

This generator acts as a helper to create a [test.guide](https://www.tracetronic.com/products/test-guide/) compatible 
test report. Specific Python classes reflecting the different elements of a test report (*TestSuite*, *TestCase* and so on)
were designed in such a way that you can create your own testsuite from these objects. This facilitates the conversion from arbitrary test report 
formats into a *.json* which test.guide can handle. With this generator, it is no more necessary to convert non-ATX formats directly
into a *.json* for test.guide. Instead, the delivered Python classes are prefilled in a simple manner, and the *.json* is
generated for you. On top of this, early format checks are conducted such that you will be notified right away if something is not
compliant to the *json* schema.

<img src="https://github.com/tracetronic/testguide_report-generator/blob/main/docs/images/Logo_TEST-GUIDE_rgb_SCREEN.png?raw=true" align="left" alt="test.guide" width="300">

test.guide is a database application for the overview, analysis and follow-up processing of test procedures, which has been specially 
developed for use in the automotive sector. It significantly facilitates the management of test resources. At the same time, it encourages 
cross-role cooperation, thereby closing the gap between test execution and test management.
<br />

**tracetronic test.guide Report Generator** project is part of
the [Automotive DevOps Platform](https://www.tracetronic.com/products/automotive-devops-platform/) by tracetronic. With
the **Automotive DevOps Platform**, we go from the big picture to the details and unite all phases of vehicle software
testing – from planning the test scopes to summarizing the test results. At the same time, continuous monitoring across
all test phases always provides an overview of all activities – even with several thousand test executions per day and
in different test environments.<br><br>


## Table of Contents

- [Installation](#installation)
- [Getting Started](#getting-started)
- [Usage](#usage)
- [Contribution](#contribution)
- [Documentation](#documentation)
- [Support](#support)
- [License](#license)

## Installation

You can directly install the project from GitHub using pip:
```bash
# HTTP
pip install git+https://github.com/tracetronic/testguide_report-generator/

# SSH
pip install git+ssh://git@github.com:tracetronic/testguide_report-generator/
```
or by adding the _testguide-report-generator_ to your dependency management file, such as [requirements.txt](https://pip.pypa.io/en/stable/reference/requirements-file-format/) or [pyproject.toml](https://python-poetry.org/docs/pyproject/).

## Getting Started

The commands which are necessary to generate [test.guide](https://www.tracetronic.com/products/test-guide/) reports are collected exemplarily in the [*example_TestSuite.py*](example_TestSuite.py). Run the example script to generate *json* and *zip* file:

```bash
python example_TestSuite.py
```

## Usage

### Assembling a TestSuite Object

The elements follow the hierarchy `TestSuite --> TestCaseFolder --> TestCase --> TestStepFolder --> TestStep`. So, instances of *TestCase(Folder)* are added to *TestSuite*, and instances of *TestStep(Folder)* are added to *TestCase*. At least one *TestCase* or *TestStep* has to be added to the respective folder (see [Restrictions](#restrictions)).

In the end, the report generator will take the assembled *TestSuite* and generate the report. The generator output is a *.json* report and a *.zip* file containing the generated test report along with possible testcase artifacts. The *.zip* file can be uploaded to test.guide via the appropriate option in test.guide. The schema of the *.json* which [test.guide](https://www.tracetronic.com/products/test-guide/) expects can be found [here](testguide_report_generator/schema/schema.json).

A small example may look like this:

```
# import necessary classes for the TestSuite creation
from testguide_report_generator.model.TestSuite import TestSuite
from testguide_report_generator.model.TestCase import TestCase, Verdict

# import the .json generator
from testguide_report_generator.ReportGenerator import Generator


def create_testsuite():

    # create the TestSuite object
    testsuite = TestSuite("All Tests", 1666698047000)

    # create the TestCase object
    testcase = TestCase("Test Brakes", 1666698047001, Verdict.FAILED)

    # add the TestCase to the TestSuite
    testsuite.add_testcase(testcase)

    # initialize the generator
    generator = Generator(testsuite)

    # execute the generator and export the result
    generator.export("output.json")

if __name__ == "__main__":
    create_testsuite()

```
A more extensive example is given in [example_TestSuite.py](example_TestSuite.py).

### Available classes and their purpose

| Class                                                                | Arguments                        | Description                                                                                                                          |
|----------------------------------------------------------------------|----------------------------------|--------------------------------------------------------------------------------------------------------------------------------------|
| [TestStep](testguide_report_generator/model/TestCase.py)             | name, verdict, (expected result) | a fundamental teststep, is added to TestCase or TestStepFolder                                                                       |
| [TestStepArtifact](testguide_report_generator/model/TestCase.py)     | filepath, type                   | artifact which gets attached directly to a teststep (such as plots)                                                                  |
| [TestStepArtifactType](testguide_report_generator/model/TestCase.py) |                                  | the type of a teststep artifact (only used with TestStepArtifact)                                                                    |
| [TestStepFolder](testguide_report_generator/model/TestCase.py)       | name                             | contains teststeps or teststep folders, is added to TestCase                                                                         |
| [TestCase](testguide_report_generator/model/TestCase.py)             | name, timestamp, verdict         | a testcase, may contain teststeps or teststep folders, as well as further specific elements; is added to TestCaseFolder or TestSuite |
| [TestCaseFolder](testguide_report_generator/model/TestCaseFolder.py) | name                             | contains testcases or testcase folders, is added to TestSuite or TestCaseFolder                                                      |
| [TestSuite](testguide_report_generator/model/TestSuite.py)           | name, timestamp                  | the testsuite, may contain TestCases or TestCaseFolder                                                                               |
| [Verdict](testguide_report_generator/model/TestCase.py)              |                                  | the verdict of the test object                                                                                                       |
| [Artifact](testguide_report_generator/model/TestCase.py)             | filepath                         | an optional artifact to an existing filepath, can be added to TestCase                                                               |
| [Parameter](testguide_report_generator/model/TestCase.py)            | name, value, direction           | a testcase parameter, can be added to TestCase                                                                                       |
| [Direction](testguide_report_generator/model/TestCase.py)            |                                  | direction of a Parameter (only used with Parameter)                                                                                  |
| [Constant](testguide_report_generator/model/TestCase.py)             | key, value                       | a test constant, can be added to TestCase                                                                                            |
| [Attribute](testguide_report_generator/model/TestCase.py)            | key, value                       | a test attribute, can be added to TestCase                                                                                           |
| [Review](testguide_report_generator/model/TestCase.py)               | comment, author, timestamp       | review, can be added to TestCase                                                                                                     |

* (): arguments in parentheses are _optional_

### Restrictions

Please note that certain requirements for the creation of the test components need to be met in order to generate a valid *.json*. These include:

* at least **one** [TestCase](testguide_report_generator/model/TestCase.py) or [TestCaseFolder](testguide_report_generator/model/TestCaseFolder.py) within a [TestSuite](testguide_report_generator/model/TestSuite.py)
* at least **one** [TestCase](testguide_report_generator/model/TestCase.py) within a [TestCaseFolder](testguide_report_generator/model/TestCaseFolder.py)
* at least **one** [TestStep](testguide_report_generator/model/TestCase.py) within a [TestStepFolder](testguide_report_generator/model/TestCase.py)
* names for [TestSuite](testguide_report_generator/model/TestSuite.py), [TestCaseFolder](testguide_report_generator/model/TestCaseFolder.py), [TestCase](testguide_report_generator/model/TestCase.py), [TestStepFolder](testguide_report_generator/model/TestCase.py) and 
[TestStep](testguide_report_generator/model/TestCase.py) between **1 - 120** characters
* [Review](testguide_report_generator/model/TestCase.py) comments between **10 - 10000** characters
* timestamps in **milliseconds** (epoch Unix time) for [TestSuite](testguide_report_generator/model/TestSuite.py) and [TestCase](testguide_report_generator/model/TestCase.py)

A complete specification can be found in the [schema](testguide_report_generator/schema/schema.json).

## Contribution

At the moment, no external contributions are intended and merge requests from forks will automatically be **rejected**! However, 
we do encourage you to file bugs and request features via the [issue tracker](https://github.com/tracetronic/testguide_report-generator/issues).

## Documentation

The documentation of the project is formatted as [reStructuredText](https://www.sphinx-doc.org/en/master/usage/restructuredtext/index.html). You can generate documentation pages from this with the help of tools such as [Sphinx](https://www.sphinx-doc.org/en/master/index.html). All necessary files are located under `docs/source`. `sphinx-apidoc` is used to generate the referenced modules'.rst files. Use `sphinx-build` to generate the documentation in the desired format,
e.g. HTML.

## Support

If you have any questions, please contact us at [support@tracetronic.com](mailto:support@tracetronic.com) and mind our [support page](https://www.tracetronic.com/infohub/support/).

## License

This plugin is licensed under MIT license. More information can be found inside the [LICENSE](LICENSE) file or within the 
[LICENSES](LICENSES) folder. Using the [REUSE helper tool](https://github.com/fsfe/reuse-tool), you can run reuse spdx to get a bill of materials.
