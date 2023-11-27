# Copyright (c) 2023 TraceTronic GmbH
#
# SPDX-License-Identifier: MIT

from unittest.mock import patch

from testguide_report_generator.util.File import get_extended_windows_path
from testguide_report_generator.util.File import get_md5_hash_from_file


def test_get_extended_windows_path_no_windows_path():
    path = "/non/windows/path"
    assert path == get_extended_windows_path(path)


def test_get_extended_windows_path_local():
    path = "C:\\this\\is\\my\\windows\\path"
    assert "\\\\?\\C:\\this\\is\\my\\windows\\path" == get_extended_windows_path(path)


@patch("os.path.realpath")
def test_get_extended_windows_path_network(os_mock):
    os_mock.side_effect = __os_mock_side_effect
    path = "\\\\my\\network\\path"

    result = get_extended_windows_path(path)

    os_mock.assert_called_once()
    assert result == "\\\\?\\UNC\\my\\network\\path"


def __os_mock_side_effect(mock_input):
    return mock_input


def test_get_md5_hash_from_file(artifact_path):
    assert "d41d8cd98f00b204e9800998ecf8427e" == get_md5_hash_from_file(artifact_path)
