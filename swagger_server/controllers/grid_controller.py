import connexion
import six
import logging

from swagger_server.models.coordinates import Coordinates  # noqa: E501
from swagger_server.models.grid import Grid  # noqa: E501
from swagger_server import util

from simulator.openDSS import OpenDSS

logging.basicConfig(format='%(asctime)s %(levelname)s %(name)s: %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__file__)

def create_grid(body):  # noqa: E501
    """Insert grid components

     # noqa: E501

    :param body: Created grid. gridID &#x3D; 0 because it is generated server-side
    :type body: dict | bytes

    :rtype: None
    """

    if connexion.request.is_json:
        logger.debug("Post grid request")
        body = Grid.from_dict(connexion.request.get_json())  # noqa: E501
        logger.info("This is the dictionary: "+ body.to_str())
        body=body.to_dict()
        load=body["loads"]
        logger.debug("Creating an instance of the simulator")
        sim=OpenDSS("Test 1")
        logger.debug("Charging the loads into the simulator")
        sim.setLoads(load)
        logger.debug("Loads charged")

    return 'do some magic!'


def delete_storage(id, body):  # noqa: E501
    """Delete storage

     # noqa: E501

    :param id: Id of the grid
    :type id: int
    :param body: Deleted grid components
    :type body: dict | bytes

    :rtype: None
    """
    if connexion.request.is_json:
        body = Grid.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'


def get_grid(id, coordinates=None):  # noqa: E501
    """Get a grid topology

    Get a grid topology by the coordinates of its entry point transformer # noqa: E501

    :param id: Id of the grid
    :type id: int
    :param coordinates: The latitude and longitude coordinates for this grids entry point
    :type coordinates: dict | bytes

    :rtype: Grid
    """
    if connexion.request.is_json:
        coordinates = Coordinates.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'


def update_storage(id, body):  # noqa: E501
    """Updated storage

     # noqa: E501

    :param id: Id of the grid
    :type id: int
    :param body: Updated grid components
    :type body: dict | bytes

    :rtype: None
    """
    if connexion.request.is_json:
        body = Grid.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'
