# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from swagger_server.models.base_model_ import Model
from swagger_server import util


class Storage(Model):
    """NOTE: This class is auto generated by the swagger code generator program.

    Do not edit the class manually.
    """

    def __init__(self, id: str=None, node: str=None, so_c: float=None, do_d: float=None, so_h: float=None, energy: float=None, inverter_efficiency: float=None, phases: int=None, voltage: float=None, voltageunit: str=None, power: float=None, powerunit: str=None, powerfactor: float=None):  # noqa: E501
        """Storage - a model defined in Swagger

        :param id: The id of this Storage.  # noqa: E501
        :type id: str
        :param node: The node of this Storage.  # noqa: E501
        :type node: str
        :param so_c: The so_c of this Storage.  # noqa: E501
        :type so_c: float
        :param do_d: The do_d of this Storage.  # noqa: E501
        :type do_d: float
        :param so_h: The so_h of this Storage.  # noqa: E501
        :type so_h: float
        :param energy: The energy of this Storage.  # noqa: E501
        :type energy: float
        :param inverter_efficiency: The inverter_efficiency of this Storage.  # noqa: E501
        :type inverter_efficiency: float
        :param phases: The phases of this Storage.  # noqa: E501
        :type phases: int
        :param voltage: The voltage of this Storage.  # noqa: E501
        :type voltage: float
        :param voltageunit: The voltageunit of this Storage.  # noqa: E501
        :type voltageunit: str
        :param power: The power of this Storage.  # noqa: E501
        :type power: float
        :param powerunit: The powerunit of this Storage.  # noqa: E501
        :type powerunit: str
        :param powerfactor: The powerfactor of this Storage.  # noqa: E501
        :type powerfactor: float
        """
        self.swagger_types = {
            'id': str,
            'node': str,
            'so_c': float,
            'do_d': float,
            'so_h': float,
            'energy': float,
            'inverter_efficiency': float,
            'phases': int,
            'voltage': float,
            'voltageunit': str,
            'power': float,
            'powerunit': str,
            'powerfactor': float
        }

        self.attribute_map = {
            'id': 'id',
            'node': 'node',
            'so_c': 'SoC',
            'do_d': 'DoD',
            'so_h': 'SoH',
            'energy': 'energy',
            'inverter_efficiency': 'inverterEfficiency',
            'phases': 'phases',
            'voltage': 'voltage',
            'voltageunit': 'voltageunit',
            'power': 'power',
            'powerunit': 'powerunit',
            'powerfactor': 'powerfactor'
        }

        self._id = id
        self._node = node
        self._so_c = so_c
        self._do_d = do_d
        self._so_h = so_h
        self._energy = energy
        self._inverter_efficiency = inverter_efficiency
        self._phases = phases
        self._voltage = voltage
        self._voltageunit = voltageunit
        self._power = power
        self._powerunit = powerunit
        self._powerfactor = powerfactor

    @classmethod
    def from_dict(cls, dikt) -> 'Storage':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The Storage of this Storage.  # noqa: E501
        :rtype: Storage
        """
        return util.deserialize_model(dikt, cls)

    @property
    def id(self) -> str:
        """Gets the id of this Storage.


        :return: The id of this Storage.
        :rtype: str
        """
        return self._id

    @id.setter
    def id(self, id: str):
        """Sets the id of this Storage.


        :param id: The id of this Storage.
        :type id: str
        """
        if id is None:
            raise ValueError("Invalid value for `id`, must not be `None`")  # noqa: E501

        self._id = id

    @property
    def node(self) -> str:
        """Gets the node of this Storage.

        ID for the connected node  # noqa: E501

        :return: The node of this Storage.
        :rtype: str
        """
        return self._node

    @node.setter
    def node(self, node: str):
        """Sets the node of this Storage.

        ID for the connected node  # noqa: E501

        :param node: The node of this Storage.
        :type node: str
        """
        if node is None:
            raise ValueError("Invalid value for `node`, must not be `None`")  # noqa: E501

        self._node = node

    @property
    def so_c(self) -> float:
        """Gets the so_c of this Storage.


        :return: The so_c of this Storage.
        :rtype: float
        """
        return self._so_c

    @so_c.setter
    def so_c(self, so_c: float):
        """Sets the so_c of this Storage.


        :param so_c: The so_c of this Storage.
        :type so_c: float
        """
        if so_c is None:
            raise ValueError("Invalid value for `so_c`, must not be `None`")  # noqa: E501

        self._so_c = so_c

    @property
    def do_d(self) -> float:
        """Gets the do_d of this Storage.


        :return: The do_d of this Storage.
        :rtype: float
        """
        return self._do_d

    @do_d.setter
    def do_d(self, do_d: float):
        """Sets the do_d of this Storage.


        :param do_d: The do_d of this Storage.
        :type do_d: float
        """
        if do_d is None:
            raise ValueError("Invalid value for `do_d`, must not be `None`")  # noqa: E501

        self._do_d = do_d

    @property
    def so_h(self) -> float:
        """Gets the so_h of this Storage.


        :return: The so_h of this Storage.
        :rtype: float
        """
        return self._so_h

    @so_h.setter
    def so_h(self, so_h: float):
        """Sets the so_h of this Storage.


        :param so_h: The so_h of this Storage.
        :type so_h: float
        """

        self._so_h = so_h

    @property
    def energy(self) -> float:
        """Gets the energy of this Storage.


        :return: The energy of this Storage.
        :rtype: float
        """
        return self._energy

    @energy.setter
    def energy(self, energy: float):
        """Sets the energy of this Storage.


        :param energy: The energy of this Storage.
        :type energy: float
        """

        self._energy = energy

    @property
    def inverter_efficiency(self) -> float:
        """Gets the inverter_efficiency of this Storage.


        :return: The inverter_efficiency of this Storage.
        :rtype: float
        """
        return self._inverter_efficiency

    @inverter_efficiency.setter
    def inverter_efficiency(self, inverter_efficiency: float):
        """Sets the inverter_efficiency of this Storage.


        :param inverter_efficiency: The inverter_efficiency of this Storage.
        :type inverter_efficiency: float
        """

        self._inverter_efficiency = inverter_efficiency

    @property
    def phases(self) -> int:
        """Gets the phases of this Storage.


        :return: The phases of this Storage.
        :rtype: int
        """
        return self._phases

    @phases.setter
    def phases(self, phases: int):
        """Sets the phases of this Storage.


        :param phases: The phases of this Storage.
        :type phases: int
        """

        self._phases = phases

    @property
    def voltage(self) -> float:
        """Gets the voltage of this Storage.


        :return: The voltage of this Storage.
        :rtype: float
        """
        return self._voltage

    @voltage.setter
    def voltage(self, voltage: float):
        """Sets the voltage of this Storage.


        :param voltage: The voltage of this Storage.
        :type voltage: float
        """

        self._voltage = voltage

    @property
    def voltageunit(self) -> str:
        """Gets the voltageunit of this Storage.


        :return: The voltageunit of this Storage.
        :rtype: str
        """
        return self._voltageunit

    @voltageunit.setter
    def voltageunit(self, voltageunit: str):
        """Sets the voltageunit of this Storage.


        :param voltageunit: The voltageunit of this Storage.
        :type voltageunit: str
        """

        self._voltageunit = voltageunit

    @property
    def power(self) -> float:
        """Gets the power of this Storage.


        :return: The power of this Storage.
        :rtype: float
        """
        return self._power

    @power.setter
    def power(self, power: float):
        """Sets the power of this Storage.


        :param power: The power of this Storage.
        :type power: float
        """

        self._power = power

    @property
    def powerunit(self) -> str:
        """Gets the powerunit of this Storage.


        :return: The powerunit of this Storage.
        :rtype: str
        """
        return self._powerunit

    @powerunit.setter
    def powerunit(self, powerunit: str):
        """Sets the powerunit of this Storage.


        :param powerunit: The powerunit of this Storage.
        :type powerunit: str
        """

        self._powerunit = powerunit

    @property
    def powerfactor(self) -> float:
        """Gets the powerfactor of this Storage.


        :return: The powerfactor of this Storage.
        :rtype: float
        """
        return self._powerfactor

    @powerfactor.setter
    def powerfactor(self, powerfactor: float):
        """Sets the powerfactor of this Storage.


        :param powerfactor: The powerfactor of this Storage.
        :type powerfactor: float
        """

        self._powerfactor = powerfactor
