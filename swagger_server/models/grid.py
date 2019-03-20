# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from swagger_server.models.base_model_ import Model
from swagger_server.models.grid_definition import GridDefinition  # noqa: F401,E501
from swagger_server.models.radial import Radial  # noqa: F401,E501
from swagger_server import util


class Grid(Model):
    """NOTE: This class is auto generated by the swagger code generator program.

    Do not edit the class manually.
    """

    def __init__(self, common: GridDefinition=None, radials: List[Radial]=None):  # noqa: E501
        """Grid - a model defined in Swagger

        :param common: The common of this Grid.  # noqa: E501
        :type common: GridDefinition
        :param radials: The radials of this Grid.  # noqa: E501
        :type radials: List[Radial]
        """
        self.swagger_types = {
            'common': GridDefinition,
            'radials': List[Radial]
        }

        self.attribute_map = {
            'common': 'common',
            'radials': 'radials'
        }

        self._common = common
        self._radials = radials

    @classmethod
    def from_dict(cls, dikt) -> 'Grid':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The Grid of this Grid.  # noqa: E501
        :rtype: Grid
        """
        return util.deserialize_model(dikt, cls)

    @property
    def common(self) -> GridDefinition:
        """Gets the common of this Grid.


        :return: The common of this Grid.
        :rtype: GridDefinition
        """
        return self._common

    @common.setter
    def common(self, common: GridDefinition):
        """Sets the common of this Grid.


        :param common: The common of this Grid.
        :type common: GridDefinition
        """

        self._common = common

    @property
    def radials(self) -> List[Radial]:
        """Gets the radials of this Grid.


        :return: The radials of this Grid.
        :rtype: List[Radial]
        """
        return self._radials

    @radials.setter
    def radials(self, radials: List[Radial]):
        """Sets the radials of this Grid.


        :param radials: The radials of this Grid.
        :type radials: List[Radial]
        """

        self._radials = radials
