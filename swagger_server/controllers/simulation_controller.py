import connexion
import six

from swagger_server.models.grid import Grid  # noqa: E501
from swagger_server import util


def create_simulation(body):  # noqa: E501
    """Send grid data to simulation engine in order to create a new simulation

     # noqa: E501

    :param body: Grid to be simulated
    :type body: dict | bytes

    :rtype: str
    """
    if connexion.request.is_json:
        body = Grid.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'


def delete_simulation(id):  # noqa: E501
    """Delete a simulation and its data

     # noqa: E501

    :param id: ID of the simulation
    :type id: str

    :rtype: None
    """
    return 'do some magic!'


def update_simulation(id, body):  # noqa: E501
    """Send new data to an existing simulation

     # noqa: E501

    :param id: ID of the simulation
    :type id: str
    :param body: Updated grid data
    :type body: dict | bytes

    :rtype: None
    """
    if connexion.request.is_json:
        body = Grid.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'
