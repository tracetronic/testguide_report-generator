# Copyright (c) 2023 TraceTronic GmbH
#
# SPDX-License-Identifier: MIT

# -*- coding: utf-8 -*-

"""
This module contains the abstract class Json2AtxRepr.
"""

from abc import ABC, abstractmethod


class Json2AtxRepr(ABC):
    """
    Interface for all data classes, which should be translated into Json.
    """

    @abstractmethod
    def create_json_repr(self):
        """
        :return: the JSON ATX representation.
        :rtype: dict
        """
        raise NotImplementedError("To be implemented")  # pragma: no cover
