# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from swagger_server.models.base_model_ import Model
from swagger_server import util


class Load(Model):
    """NOTE: This class is auto generated by the swagger code generator program.

    Do not edit the class manually.
    """

    def __init__(self, id: str=None, bus: str=None, phases: int=None, connection_type: str=None, model: int=None, k_v: float=None, k_w: float=None, k_var: float=None):  # noqa: E501
        """Load - a model defined in Swagger

        :param id: The id of this Load.  # noqa: E501
        :type id: str
        :param bus: The bus of this Load.  # noqa: E501
        :type bus: str
        :param phases: The phases of this Load.  # noqa: E501
        :type phases: int
        :param connection_type: The connection_type of this Load.  # noqa: E501
        :type connection_type: str
        :param model: The model of this Load.  # noqa: E501
        :type model: int
        :param k_v: The k_v of this Load.  # noqa: E501
        :type k_v: float
        :param k_w: The k_w of this Load.  # noqa: E501
        :type k_w: float
        :param k_var: The k_var of this Load.  # noqa: E501
        :type k_var: float
        """
        self.swagger_types = {
            'id': str,
            'bus': str,
            'phases': int,
            'connection_type': str,
            'model': int,
            'k_v': float,
            'k_w': float,
            'k_var': float
        }

        self.attribute_map = {
            'id': 'id',
            'bus': 'bus',
            'phases': 'phases',
            'connection_type': 'connection_type',
            'model': 'model',
            'k_v': 'kV',
            'k_w': 'kW',
            'k_var': 'kVar'
        }

        self._id = id
        self._bus = bus
        self._phases = phases
        self._connection_type = connection_type
        self._model = model
        self._k_v = k_v
        self._k_w = k_w
        self._k_var = k_var

    @classmethod
    def from_dict(cls, dikt) -> 'Load':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The Load of this Load.  # noqa: E501
        :rtype: Load
        """
        return util.deserialize_model(dikt, cls)

    @property
    def id(self) -> str:
        """Gets the id of this Load.


        :return: The id of this Load.
        :rtype: str
        """
        return self._id

    @id.setter
    def id(self, id: str):
        """Sets the id of this Load.


        :param id: The id of this Load.
        :type id: str
        """
        if id is None:
            raise ValueError("Invalid value for `id`, must not be `None`")  # noqa: E501

        self._id = id

    @property
    def bus(self) -> str:
        """Gets the bus of this Load.

        ID for the connected node  # noqa: E501

        :return: The bus of this Load.
        :rtype: str
        """
        return self._bus

    @bus.setter
    def bus(self, bus: str):
        """Sets the bus of this Load.

        ID for the connected node  # noqa: E501

        :param bus: The bus of this Load.
        :type bus: str
        """
        if bus is None:
            raise ValueError("Invalid value for `bus`, must not be `None`")  # noqa: E501

        self._bus = bus

    @property
    def phases(self) -> int:
        """Gets the phases of this Load.


        :return: The phases of this Load.
        :rtype: int
        """
        return self._phases

    @phases.setter
    def phases(self, phases: int):
        """Sets the phases of this Load.


        :param phases: The phases of this Load.
        :type phases: int
        """
        if phases is None:
            raise ValueError("Invalid value for `phases`, must not be `None`")  # noqa: E501

        self._phases = phases

    @property
    def connection_type(self) -> str:
        """Gets the connection_type of this Load.


        :return: The connection_type of this Load.
        :rtype: str
        """
        return self._connection_type

    @connection_type.setter
    def connection_type(self, connection_type: str):
        """Sets the connection_type of this Load.


        :param connection_type: The connection_type of this Load.
        :type connection_type: str
        """

        self._connection_type = connection_type

    @property
    def model(self) -> int:
        """Gets the model of this Load.

        Defining load models for openDSS  # noqa: E501

        :return: The model of this Load.
        :rtype: int
        """
        return self._model

    @model.setter
    def model(self, model: int):
        """Sets the model of this Load.

        Defining load models for openDSS  # noqa: E501

        :param model: The model of this Load.
        :type model: int
        """
        if model is not None and model > 8:  # noqa: E501
            raise ValueError("Invalid value for `model`, must be a value less than or equal to `8`")  # noqa: E501
        if model is not None and model < 1:  # noqa: E501
            raise ValueError("Invalid value for `model`, must be a value greater than or equal to `1`")  # noqa: E501

        self._model = model

    @property
    def k_v(self) -> float:
        """Gets the k_v of this Load.


        :return: The k_v of this Load.
        :rtype: float
        """
        return self._k_v

    @k_v.setter
    def k_v(self, k_v: float):
        """Sets the k_v of this Load.


        :param k_v: The k_v of this Load.
        :type k_v: float
        """
        if k_v is None:
            raise ValueError("Invalid value for `k_v`, must not be `None`")  # noqa: E501

        self._k_v = k_v

    @property
    def k_w(self) -> float:
        """Gets the k_w of this Load.


        :return: The k_w of this Load.
        :rtype: float
        """
        return self._k_w

    @k_w.setter
    def k_w(self, k_w: float):
        """Sets the k_w of this Load.


        :param k_w: The k_w of this Load.
        :type k_w: float
        """

        self._k_w = k_w

    @property
    def k_var(self) -> float:
        """Gets the k_var of this Load.


        :return: The k_var of this Load.
        :rtype: float
        """
        return self._k_var

    @k_var.setter
    def k_var(self, k_var: float):
        """Sets the k_var of this Load.


        :param k_var: The k_var of this Load.
        :type k_var: float
        """

        self._k_var = k_var
