# Copyright (c) 2023-2024 tracetronic GmbH
#
# SPDX-License-Identifier: MIT

import argparse
import toml
import requests
import json

REPO_USER = "tracetronic"
REPO_NAME = "testguide_report-generator"


def _bump_up_version():
    try:
        with open("pyproject.toml", "r") as file:
            toml_obj = toml.load(file)

        current_version = toml_obj.get("tool").get("poetry").get("version")
        versions = current_version.split(".")

        next_version = versions[0] + "." + str(int(versions[1]) + 1) + "-beta"
        print(next_version)  # echo

        toml_obj["tool"]["poetry"]["version"] = next_version
        with open("pyproject.toml", "w") as file:
            toml.dump(toml_obj, file)

        return 0

    except OSError:
        print("Something went wrong during .toml processing. Aborting...")
        return 1


def _publish_latest_release_draft(token):
    if token is None:
        raise TypeError("Argument 'token' must not be None! Aborting...")

    headers = {"Accept": "application/vnd.github+json", "Authorization": f"Bearer {token}",
               "X-GitHub-Api-Version": "2022-11-28"}

    # first, get the latest Release (which should be set to "draft" - otherwise, something is wrong)
    url = f"https://api.github.com/repos/{REPO_USER}/{REPO_NAME}/releases"

    response = requests.get(url + "?per_page=1", allow_redirects=True, headers=headers).json()

    release_id = response[0].get("id")
    is_draft = response[0].get("draft")

    if not is_draft:
        raise ValueError("Release is not a draft. Cannot publish. Aborting...")

    ########################################

    # set this Release not to be a draft
    data_dict = {"draft": "false", "prerelease": "false"}

    response = requests.patch(url=url + f"/{release_id}", headers=headers, data=json.dumps(data_dict),
                              allow_redirects=True)

    return 0 if response.status_code == 200 else 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog='Automation Scripts for GitHub repositories',
        description='Helps doing some GitHub workflows automatically.'
    )
    parser.add_argument('-n', '--name', required=True)
    parser.add_argument('-t', '--token', required=False)
    args = parser.parse_args()

    if args.name == "bump_up_version":
        _bump_up_version()

    elif args.name == "publish_latest_release_draft":
        _publish_latest_release_draft(args.token)

    else:
        raise ValueError("Unknown script name. Aborting...")
