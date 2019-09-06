# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from swagger_server.models.base_model_ import Model
from swagger_server import util


class ElectricVehicle(Model):
    """NOTE: This class is auto generated by the swagger code generator program.

    Do not edit the class manually.
    """

    def __init__(self, id: str=None, so_c: float=None, battery_capacity_k_wh: float=None, unit_consumption_assumption: float=5.0, unit_drop_penalty: float=None):  # noqa: E501
        """ElectricVehicle - a model defined in Swagger

        :param id: The id of this ElectricVehicle.  # noqa: E501
        :type id: str
        :param so_c: The so_c of this ElectricVehicle.  # noqa: E501
        :type so_c: float
        :param battery_capacity_k_wh: The battery_capacity_k_wh of this ElectricVehicle.  # noqa: E501
        :type battery_capacity_k_wh: float
        :param unit_consumption_assumption: The unit_consumption_assumption of this ElectricVehicle.  # noqa: E501
        :type unit_consumption_assumption: float
        :param unit_drop_penalty: The unit_drop_penalty of this ElectricVehicle.  # noqa: E501
        :type unit_drop_penalty: float
        """
        self.swagger_types = {
            'id': str,
            'so_c': float,
            'battery_capacity_k_wh': float,
            'unit_consumption_assumption': float,
            'unit_drop_penalty': float
        }

        self.attribute_map = {
            'id': 'id',
            'so_c': 'SoC',
            'battery_capacity_k_wh': 'battery_capacity_kWh',
            'unit_consumption_assumption': 'unit_consumption_assumption',
            'unit_drop_penalty': 'unit_drop_penalty'
        }

        self._id = id
        self._so_c = so_c
        self._battery_capacity_k_wh = battery_capacity_k_wh
        self._unit_consumption_assumption = unit_consumption_assumption
        self._unit_drop_penalty = unit_drop_penalty

    @classmethod
    def from_dict(cls, dikt) -> 'ElectricVehicle':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The ElectricVehicle of this ElectricVehicle.  # noqa: E501
        :rtype: ElectricVehicle
        """
        return util.deserialize_model(dikt, cls)

    @property
    def id(self) -> str:
        """Gets the id of this ElectricVehicle.


        :return: The id of this ElectricVehicle.
        :rtype: str
        """
        return self._id

    @id.setter
    def id(self, id: str):
        """Sets the id of this ElectricVehicle.


        :param id: The id of this ElectricVehicle.
        :type id: str
        """
        if id is None:
            raise ValueError("Invalid value for `id`, must not be `None`")  # noqa: E501

        self._id = id

    @property
    def so_c(self) -> float:
        """Gets the so_c of this ElectricVehicle.


        :return: The so_c of this ElectricVehicle.
        :rtype: float
        """
        return self._so_c

    @so_c.setter
    def so_c(self, so_c: float):
        """Sets the so_c of this ElectricVehicle.


        :param so_c: The so_c of this ElectricVehicle.
        :type so_c: float
        """
        if so_c is None:
            raise ValueError("Invalid value for `so_c`, must not be `None`")  # noqa: E501
        if so_c is not None and so_c > 100:  # noqa: E501
            raise ValueError("Invalid value for `so_c`, must be a value less than or equal to `100`")  # noqa: E501
        if so_c is not None and so_c < 0:  # noqa: E501
            raise ValueError("Invalid value for `so_c`, must be a value greater than or equal to `0`")  # noqa: E501

        self._so_c = so_c

    @property
    def battery_capacity_k_wh(self) -> float:
        """Gets the battery_capacity_k_wh of this ElectricVehicle.


        :return: The battery_capacity_k_wh of this ElectricVehicle.
        :rtype: float
        """
        return self._battery_capacity_k_wh

    @battery_capacity_k_wh.setter
    def battery_capacity_k_wh(self, battery_capacity_k_wh: float):
        """Sets the battery_capacity_k_wh of this ElectricVehicle.


        :param battery_capacity_k_wh: The battery_capacity_k_wh of this ElectricVehicle.
        :type battery_capacity_k_wh: float
        """
        if battery_capacity_k_wh is None:
            raise ValueError("Invalid value for `battery_capacity_k_wh`, must not be `None`")  # noqa: E501

        self._battery_capacity_k_wh = battery_capacity_k_wh

    @property
    def unit_consumption_assumption(self) -> float:
        """Gets the unit_consumption_assumption of this ElectricVehicle.


        :return: The unit_consumption_assumption of this ElectricVehicle.
        :rtype: float
        """
        return self._unit_consumption_assumption

    @unit_consumption_assumption.setter
    def unit_consumption_assumption(self, unit_consumption_assumption: float):
        """Sets the unit_consumption_assumption of this ElectricVehicle.


        :param unit_consumption_assumption: The unit_consumption_assumption of this ElectricVehicle.
        :type unit_consumption_assumption: float
        """

        self._unit_consumption_assumption = unit_consumption_assumption

    @property
    def unit_drop_penalty(self) -> float:
        """Gets the unit_drop_penalty of this ElectricVehicle.


        :return: The unit_drop_penalty of this ElectricVehicle.
        :rtype: float
        """
        return self._unit_drop_penalty

    @unit_drop_penalty.setter
    def unit_drop_penalty(self, unit_drop_penalty: float):
        """Sets the unit_drop_penalty of this ElectricVehicle.


        :param unit_drop_penalty: The unit_drop_penalty of this ElectricVehicle.
        :type unit_drop_penalty: float
        """

        self._unit_drop_penalty = unit_drop_penalty