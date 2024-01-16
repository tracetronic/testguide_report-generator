# Copyright (c) 2023-2024 tracetronic GmbH
#
# SPDX-License-Identifier: MIT

import json
import os
import pytest
import requests
from urllib.parse import urlparse, parse_qs

from conftest import ValueStorage
from tests.e2e.e2e_testsuite import create_testsuite


@pytest.mark.skipif(os.environ.get("TEST_GUIDE_URL") is None, reason="Env variables are not set")
def test_upload(value_storage: ValueStorage):
    """
    Uploads a test suite with all classes to test.guide
    """
    create_testsuite()
    assert os.path.exists("e2e.json")
    assert os.path.exists("e2e.zip")

    upload_url = value_storage.BASE_URL + "api/upload-file"
    params = {
        "projectId": value_storage.PROJECT_ID,
        "authKey": value_storage.AUTHKEY,
        "apiVersion": "up-to-date",
        "converter": "json2atx",
    }

    filename = os.path.basename("./e2e.zip")
    uploadFile = {"file-upload": (filename, open("./e2e.zip", "rb"), "application/zip")}
    r = requests.post(
        upload_url,
        params=params,
        files=uploadFile,
        verify=False,
        headers={
            "accept": "application/json",
        },
    )
    assert r.ok
    for elem in r.json()["ENTRIES"]:
        if "atxId" in elem["TEXT"]:
            url = elem["TEXT"]
            parsed_url = urlparse(url)
            value_storage.e2e_atxid = parse_qs(parsed_url.query)["atxId"][0]

    assert value_storage.e2e_atxid is not None


@pytest.mark.skipif(os.environ.get("TEST_GUIDE_URL") is None, reason="Env variables are not set")
def test_download(value_storage: ValueStorage):
    """
    Test downloads data from test.guide
    """
    query_url = value_storage.BASE_URL + "api/report/testCaseExecutions/filter"
    params = {"projectId": value_storage.PROJECT_ID, "offset": 0, "limit": 100, "authKey": value_storage.AUTHKEY}
    filter = {
        "atxIds": [value_storage.e2e_atxid],
    }
    r = requests.post(
        query_url,
        headers={
            "Content-Type": "application/json",
            "accept": "application/json",
        },
        params=params,
        data=json.dumps(filter),
        verify=False,
    )
    assert r.status_code == 200
    value_storage.remote_testcases_json = r.json()


@pytest.mark.skipif(os.environ.get("TEST_GUIDE_URL") is None, reason="Env variables are not set")
def test_compare(value_storage):
    """
    Test compares data generated with data downloaded from test.guide
    """
    assert value_storage.remote_testcases_json is not None
    f = open("e2e.json")
    data = json.load(f)
    local_testcases = []
    testcases = [data["testcases"]]
    while testcases:
        current_folder = testcases.pop()
        for item in current_folder:
            if item["@type"] == "testcasefolder":
                testcases.append(item["testcases"])
            else:
                local_testcases.append(item)

    assert len(value_storage.remote_testcases_json) == len(local_testcases)
    for remote_testcase in value_storage.remote_testcases_json:
        for local_testcase in local_testcases:
            if local_testcase["name"] == remote_testcase["testCaseName"]:
                assert local_testcase["verdict"] == remote_testcase["verdict"]
                assert local_testcase["paramSet"] == remote_testcase["parameterSet"]
                assert len(local_testcase["parameters"]) == len(remote_testcase["parameters"])
                assert len(local_testcase["setupTestSteps"]) == len(remote_testcase["testSteps"]["setup"])
                assert len(local_testcase["executionTestSteps"]) == len(remote_testcase["testSteps"]["execution"])
                assert len(local_testcase["teardownTestSteps"]) == len(remote_testcase["testSteps"]["teardown"])
                assert len(local_testcase["attributes"]) == len(remote_testcase["attributes"])
                assert len(local_testcase["constants"]) == len(remote_testcase["constants"])
                if "review" in local_testcase:
                    assert local_testcase["review"]["comment"] == remote_testcase["lastReview"]["comment"]
                assert remote_testcase["testSuiteName"] == data["name"]
                break
