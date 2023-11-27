# Copyright (c) 2023 TraceTronic GmbH
#
# SPDX-License-Identifier: MIT

# -*- coding: utf-8 -*-

"""
This module contains some utility methods.
"""

import hashlib
import os


def get_extended_windows_path(source_path: str):
    """
    Appends the extension to the transferred path so that Windows can also handle path lengths of
    more than 255 characters. UNC paths are explicitly considered separately.

    :param source_path: Path to be extended.
    :type source_path: str
    :return: Windows path with the extension for more than 255 characters path length.
    :rtype: str
    """
    if len(source_path) >= 2:
        # if path is local non-UNC, extend to local UNC
        if source_path[1] == ":":
            real_path = os.path.normpath(source_path)
            source_path = "\\\\?\\" + real_path
        # if path is UNC network resource
        elif source_path.startswith("\\\\") and not source_path.startswith("\\\\?\\"):
            source_path = "\\\\?\\UNC\\" + source_path.lstrip("\\")
            source_path = os.path.realpath(source_path)
    return source_path


def get_md5_hash_from_file(file_path):
    """
    Calculates the MD5 hash of the file.

    :param file_path: file path
    :type file_path: str
    :return: MD5 hash
    :rtype: str
    """
    hasher = hashlib.md5()
    with open(get_extended_windows_path(file_path), 'rb') as afile:
        buf = afile.read()
        hasher.update(buf)
    return hasher.hexdigest()
