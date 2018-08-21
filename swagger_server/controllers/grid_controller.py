import connexion
import six
import logging

from swagger_server.models.coordinates import Coordinates  # noqa: E501
from swagger_server.models.grid import Grid  # noqa: E501
from swagger_server import util

from data_management.controller import gridController as gControl


logging.basicConfig(format='%(asctime)s %(levelname)s %(name)s: %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__file__)



def get_grid(locationName):  # noqa: E501
    """Get the full grid topology

    Get a grid topology (all transformers) for a specific geolocation (e.g. Fur) # noqa: E501

    :param locationName: Textual identifier for the geolocation (e.g. Fur)
    :type locationName: str

    :rtype: List[Transformer]
    """
    return 'do some magic!'

