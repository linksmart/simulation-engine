# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from swagger_server.models.base_model_ import Model
from swagger_server import util


class Powerline(Model):
    """NOTE: This class is auto generated by the swagger code generator program.

    Do not edit the class manually.
    """

    def __init__(self, id: str=None, node1: str=None, node2: str=None, req: float=None, xeq: float=None, ceq_tot: float=None, phases: int=None, length: float=None, unitlength: str=None, linecode: str=None):  # noqa: E501
        """Powerline - a model defined in Swagger

        :param id: The id of this Powerline.  # noqa: E501
        :type id: str
        :param node1: The node1 of this Powerline.  # noqa: E501
        :type node1: str
        :param node2: The node2 of this Powerline.  # noqa: E501
        :type node2: str
        :param req: The req of this Powerline.  # noqa: E501
        :type req: float
        :param xeq: The xeq of this Powerline.  # noqa: E501
        :type xeq: float
        :param ceq_tot: The ceq_tot of this Powerline.  # noqa: E501
        :type ceq_tot: float
        :param phases: The phases of this Powerline.  # noqa: E501
        :type phases: int
        :param length: The length of this Powerline.  # noqa: E501
        :type length: float
        :param unitlength: The unitlength of this Powerline.  # noqa: E501
        :type unitlength: str
        :param linecode: The linecode of this Powerline.  # noqa: E501
        :type linecode: str
        """
        self.swagger_types = {
            'id': str,
            'node1': str,
            'node2': str,
            'req': float,
            'xeq': float,
            'ceq_tot': float,
            'phases': int,
            'length': float,
            'unitlength': str,
            'linecode': str
        }

        self.attribute_map = {
            'id': 'id',
            'node1': 'node1',
            'node2': 'node2',
            'req': 'Req',
            'xeq': 'Xeq',
            'ceq_tot': 'CeqTot',
            'phases': 'phases',
            'length': 'length',
            'unitlength': 'unitlength',
            'linecode': 'linecode'
        }

        self._id = id
        self._node1 = node1
        self._node2 = node2
        self._req = req
        self._xeq = xeq
        self._ceq_tot = ceq_tot
        self._phases = phases
        self._length = length
        self._unitlength = unitlength
        self._linecode = linecode

    @classmethod
    def from_dict(cls, dikt) -> 'Powerline':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The Powerline of this Powerline.  # noqa: E501
        :rtype: Powerline
        """
        return util.deserialize_model(dikt, cls)

    @property
    def id(self) -> str:
        """Gets the id of this Powerline.


        :return: The id of this Powerline.
        :rtype: str
        """
        return self._id

    @id.setter
    def id(self, id: str):
        """Sets the id of this Powerline.


        :param id: The id of this Powerline.
        :type id: str
        """
        if id is None:
            raise ValueError("Invalid value for `id`, must not be `None`")  # noqa: E501

        self._id = id

    @property
    def node1(self) -> str:
        """Gets the node1 of this Powerline.

        ID for the connected node  # noqa: E501

        :return: The node1 of this Powerline.
        :rtype: str
        """
        return self._node1

    @node1.setter
    def node1(self, node1: str):
        """Sets the node1 of this Powerline.

        ID for the connected node  # noqa: E501

        :param node1: The node1 of this Powerline.
        :type node1: str
        """
        if node1 is None:
            raise ValueError("Invalid value for `node1`, must not be `None`")  # noqa: E501

        self._node1 = node1

    @property
    def node2(self) -> str:
        """Gets the node2 of this Powerline.

        ID for the connected node  # noqa: E501

        :return: The node2 of this Powerline.
        :rtype: str
        """
        return self._node2

    @node2.setter
    def node2(self, node2: str):
        """Sets the node2 of this Powerline.

        ID for the connected node  # noqa: E501

        :param node2: The node2 of this Powerline.
        :type node2: str
        """
        if node2 is None:
            raise ValueError("Invalid value for `node2`, must not be `None`")  # noqa: E501

        self._node2 = node2

    @property
    def req(self) -> float:
        """Gets the req of this Powerline.


        :return: The req of this Powerline.
        :rtype: float
        """
        return self._req

    @req.setter
    def req(self, req: float):
        """Sets the req of this Powerline.


        :param req: The req of this Powerline.
        :type req: float
        """

        self._req = req

    @property
    def xeq(self) -> float:
        """Gets the xeq of this Powerline.


        :return: The xeq of this Powerline.
        :rtype: float
        """
        return self._xeq

    @xeq.setter
    def xeq(self, xeq: float):
        """Sets the xeq of this Powerline.


        :param xeq: The xeq of this Powerline.
        :type xeq: float
        """

        self._xeq = xeq

    @property
    def ceq_tot(self) -> float:
        """Gets the ceq_tot of this Powerline.


        :return: The ceq_tot of this Powerline.
        :rtype: float
        """
        return self._ceq_tot

    @ceq_tot.setter
    def ceq_tot(self, ceq_tot: float):
        """Sets the ceq_tot of this Powerline.


        :param ceq_tot: The ceq_tot of this Powerline.
        :type ceq_tot: float
        """

        self._ceq_tot = ceq_tot

    @property
    def phases(self) -> int:
        """Gets the phases of this Powerline.


        :return: The phases of this Powerline.
        :rtype: int
        """
        return self._phases

    @phases.setter
    def phases(self, phases: int):
        """Sets the phases of this Powerline.


        :param phases: The phases of this Powerline.
        :type phases: int
        """

        self._phases = phases

    @property
    def length(self) -> float:
        """Gets the length of this Powerline.


        :return: The length of this Powerline.
        :rtype: float
        """
        return self._length

    @length.setter
    def length(self, length: float):
        """Sets the length of this Powerline.


        :param length: The length of this Powerline.
        :type length: float
        """
        if length is None:
            raise ValueError("Invalid value for `length`, must not be `None`")  # noqa: E501

        self._length = length

    @property
    def unitlength(self) -> str:
        """Gets the unitlength of this Powerline.


        :return: The unitlength of this Powerline.
        :rtype: str
        """
        return self._unitlength

    @unitlength.setter
    def unitlength(self, unitlength: str):
        """Sets the unitlength of this Powerline.


        :param unitlength: The unitlength of this Powerline.
        :type unitlength: str
        """
        if unitlength is None:
            raise ValueError("Invalid value for `unitlength`, must not be `None`")  # noqa: E501

        self._unitlength = unitlength

    @property
    def linecode(self) -> str:
        """Gets the linecode of this Powerline.


        :return: The linecode of this Powerline.
        :rtype: str
        """
        return self._linecode

    @linecode.setter
    def linecode(self, linecode: str):
        """Sets the linecode of this Powerline.


        :param linecode: The linecode of this Powerline.
        :type linecode: str
        """

        self._linecode = linecode
