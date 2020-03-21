# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from swagger_server.models.base_model_ import Model
from swagger_server import util


class GridDefinition(Model):
    """NOTE: This class is auto generated by the swagger code generator program.

    Do not edit the class manually.
    """

    def __init__(self, id: str=None, base_k_v: float=None, per_unit: float=None, phases: int=None, bus1: str=None, angle: int=None, mv_asc3: float=None, mv_asc1: float=None, base_frequency: int=None, voltage_bases: List[float]=None, url_storage_controller: str='http://localhost:8080', city: str=None, country: str=None, simulation_initial_timestamp: int=None):  # noqa: E501
        """GridDefinition - a model defined in Swagger

        :param id: The id of this GridDefinition.  # noqa: E501
        :type id: str
        :param base_k_v: The base_k_v of this GridDefinition.  # noqa: E501
        :type base_k_v: float
        :param per_unit: The per_unit of this GridDefinition.  # noqa: E501
        :type per_unit: float
        :param phases: The phases of this GridDefinition.  # noqa: E501
        :type phases: int
        :param bus1: The bus1 of this GridDefinition.  # noqa: E501
        :type bus1: str
        :param angle: The angle of this GridDefinition.  # noqa: E501
        :type angle: int
        :param mv_asc3: The mv_asc3 of this GridDefinition.  # noqa: E501
        :type mv_asc3: float
        :param mv_asc1: The mv_asc1 of this GridDefinition.  # noqa: E501
        :type mv_asc1: float
        :param base_frequency: The base_frequency of this GridDefinition.  # noqa: E501
        :type base_frequency: int
        :param voltage_bases: The voltage_bases of this GridDefinition.  # noqa: E501
        :type voltage_bases: List[float]
        :param url_storage_controller: The url_storage_controller of this GridDefinition.  # noqa: E501
        :type url_storage_controller: str
        :param city: The city of this GridDefinition.  # noqa: E501
        :type city: str
        :param country: The country of this GridDefinition.  # noqa: E501
        :type country: str
        :param simulation_initial_timestamp: The simulation_initial_timestamp of this GridDefinition.  # noqa: E501
        :type simulation_initial_timestamp: int
        """
        self.swagger_types = {
            'id': str,
            'base_k_v': float,
            'per_unit': float,
            'phases': int,
            'bus1': str,
            'angle': int,
            'mv_asc3': float,
            'mv_asc1': float,
            'base_frequency': int,
            'voltage_bases': List[float],
            'url_storage_controller': str,
            'city': str,
            'country': str,
            'simulation_initial_timestamp': int
        }

        self.attribute_map = {
            'id': 'id',
            'base_k_v': 'base_kV',
            'per_unit': 'per_unit',
            'phases': 'phases',
            'bus1': 'bus1',
            'angle': 'angle',
            'mv_asc3': 'MVAsc3',
            'mv_asc1': 'MVAsc1',
            'base_frequency': 'base_frequency',
            'voltage_bases': 'VoltageBases',
            'url_storage_controller': 'url_storage_controller',
            'city': 'city',
            'country': 'country',
            'simulation_initial_timestamp': 'simulation_initial_timestamp'
        }

        self._id = id
        self._base_k_v = base_k_v
        self._per_unit = per_unit
        self._phases = phases
        self._bus1 = bus1
        self._angle = angle
        self._mv_asc3 = mv_asc3
        self._mv_asc1 = mv_asc1
        self._base_frequency = base_frequency
        self._voltage_bases = voltage_bases
        self._url_storage_controller = url_storage_controller
        self._city = city
        self._country = country
        self._simulation_initial_timestamp = simulation_initial_timestamp

    @classmethod
    def from_dict(cls, dikt) -> 'GridDefinition':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The Grid_Definition of this GridDefinition.  # noqa: E501
        :rtype: GridDefinition
        """
        return util.deserialize_model(dikt, cls)

    @property
    def id(self) -> str:
        """Gets the id of this GridDefinition.


        :return: The id of this GridDefinition.
        :rtype: str
        """
        return self._id

    @id.setter
    def id(self, id: str):
        """Sets the id of this GridDefinition.


        :param id: The id of this GridDefinition.
        :type id: str
        """
        if id is None:
            raise ValueError("Invalid value for `id`, must not be `None`")  # noqa: E501

        self._id = id

    @property
    def base_k_v(self) -> float:
        """Gets the base_k_v of this GridDefinition.


        :return: The base_k_v of this GridDefinition.
        :rtype: float
        """
        return self._base_k_v

    @base_k_v.setter
    def base_k_v(self, base_k_v: float):
        """Sets the base_k_v of this GridDefinition.


        :param base_k_v: The base_k_v of this GridDefinition.
        :type base_k_v: float
        """
        if base_k_v is None:
            raise ValueError("Invalid value for `base_k_v`, must not be `None`")  # noqa: E501

        self._base_k_v = base_k_v

    @property
    def per_unit(self) -> float:
        """Gets the per_unit of this GridDefinition.


        :return: The per_unit of this GridDefinition.
        :rtype: float
        """
        return self._per_unit

    @per_unit.setter
    def per_unit(self, per_unit: float):
        """Sets the per_unit of this GridDefinition.


        :param per_unit: The per_unit of this GridDefinition.
        :type per_unit: float
        """

        self._per_unit = per_unit

    @property
    def phases(self) -> int:
        """Gets the phases of this GridDefinition.


        :return: The phases of this GridDefinition.
        :rtype: int
        """
        return self._phases

    @phases.setter
    def phases(self, phases: int):
        """Sets the phases of this GridDefinition.


        :param phases: The phases of this GridDefinition.
        :type phases: int
        """
        if phases is None:
            raise ValueError("Invalid value for `phases`, must not be `None`")  # noqa: E501

        self._phases = phases

    @property
    def bus1(self) -> str:
        """Gets the bus1 of this GridDefinition.


        :return: The bus1 of this GridDefinition.
        :rtype: str
        """
        return self._bus1

    @bus1.setter
    def bus1(self, bus1: str):
        """Sets the bus1 of this GridDefinition.


        :param bus1: The bus1 of this GridDefinition.
        :type bus1: str
        """
        if bus1 is None:
            raise ValueError("Invalid value for `bus1`, must not be `None`")  # noqa: E501

        self._bus1 = bus1

    @property
    def angle(self) -> int:
        """Gets the angle of this GridDefinition.


        :return: The angle of this GridDefinition.
        :rtype: int
        """
        return self._angle

    @angle.setter
    def angle(self, angle: int):
        """Sets the angle of this GridDefinition.


        :param angle: The angle of this GridDefinition.
        :type angle: int
        """
        if angle is None:
            raise ValueError("Invalid value for `angle`, must not be `None`")  # noqa: E501

        self._angle = angle

    @property
    def mv_asc3(self) -> float:
        """Gets the mv_asc3 of this GridDefinition.


        :return: The mv_asc3 of this GridDefinition.
        :rtype: float
        """
        return self._mv_asc3

    @mv_asc3.setter
    def mv_asc3(self, mv_asc3: float):
        """Sets the mv_asc3 of this GridDefinition.


        :param mv_asc3: The mv_asc3 of this GridDefinition.
        :type mv_asc3: float
        """
        if mv_asc3 is None:
            raise ValueError("Invalid value for `mv_asc3`, must not be `None`")  # noqa: E501

        self._mv_asc3 = mv_asc3

    @property
    def mv_asc1(self) -> float:
        """Gets the mv_asc1 of this GridDefinition.


        :return: The mv_asc1 of this GridDefinition.
        :rtype: float
        """
        return self._mv_asc1

    @mv_asc1.setter
    def mv_asc1(self, mv_asc1: float):
        """Sets the mv_asc1 of this GridDefinition.


        :param mv_asc1: The mv_asc1 of this GridDefinition.
        :type mv_asc1: float
        """

        self._mv_asc1 = mv_asc1

    @property
    def base_frequency(self) -> int:
        """Gets the base_frequency of this GridDefinition.


        :return: The base_frequency of this GridDefinition.
        :rtype: int
        """
        return self._base_frequency

    @base_frequency.setter
    def base_frequency(self, base_frequency: int):
        """Sets the base_frequency of this GridDefinition.


        :param base_frequency: The base_frequency of this GridDefinition.
        :type base_frequency: int
        """
        if base_frequency is None:
            raise ValueError("Invalid value for `base_frequency`, must not be `None`")  # noqa: E501

        self._base_frequency = base_frequency

    @property
    def voltage_bases(self) -> List[float]:
        """Gets the voltage_bases of this GridDefinition.


        :return: The voltage_bases of this GridDefinition.
        :rtype: List[float]
        """
        return self._voltage_bases

    @voltage_bases.setter
    def voltage_bases(self, voltage_bases: List[float]):
        """Sets the voltage_bases of this GridDefinition.


        :param voltage_bases: The voltage_bases of this GridDefinition.
        :type voltage_bases: List[float]
        """
        if voltage_bases is None:
            raise ValueError("Invalid value for `voltage_bases`, must not be `None`")  # noqa: E501

        self._voltage_bases = voltage_bases

    @property
    def url_storage_controller(self) -> str:
        """Gets the url_storage_controller of this GridDefinition.


        :return: The url_storage_controller of this GridDefinition.
        :rtype: str
        """
        return self._url_storage_controller

    @url_storage_controller.setter
    def url_storage_controller(self, url_storage_controller: str):
        """Sets the url_storage_controller of this GridDefinition.


        :param url_storage_controller: The url_storage_controller of this GridDefinition.
        :type url_storage_controller: str
        """

        self._url_storage_controller = url_storage_controller

    @property
    def city(self) -> str:
        """Gets the city of this GridDefinition.


        :return: The city of this GridDefinition.
        :rtype: str
        """
        return self._city

    @city.setter
    def city(self, city: str):
        """Sets the city of this GridDefinition.


        :param city: The city of this GridDefinition.
        :type city: str
        """

        self._city = city

    @property
    def country(self) -> str:
        """Gets the country of this GridDefinition.


        :return: The country of this GridDefinition.
        :rtype: str
        """
        return self._country

    @country.setter
    def country(self, country: str):
        """Sets the country of this GridDefinition.


        :param country: The country of this GridDefinition.
        :type country: str
        """

        self._country = country

    @property
    def simulation_initial_timestamp(self) -> int:
        """Gets the simulation_initial_timestamp of this GridDefinition.


        :return: The simulation_initial_timestamp of this GridDefinition.
        :rtype: int
        """
        return self._simulation_initial_timestamp

    @simulation_initial_timestamp.setter
    def simulation_initial_timestamp(self, simulation_initial_timestamp: int):
        """Sets the simulation_initial_timestamp of this GridDefinition.


        :param simulation_initial_timestamp: The simulation_initial_timestamp of this GridDefinition.
        :type simulation_initial_timestamp: int
        """

        self._simulation_initial_timestamp = simulation_initial_timestamp
