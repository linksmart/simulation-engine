import connexion
import six
import logging
from flask import json

from swagger_server.models.simulation import Simulation  # noqa: E501
from swagger_server.models.simulation_result import SimulationResult  # noqa: E501
from swagger_server import util

logging.basicConfig(format='%(asctime)s %(levelname)s %(name)s: %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__file__)

	
def run_simulation(body):  # noqa: E501
    """Runs a simulation

     # noqa: E501

    :param body: Run a simulation
    :type body: dict | bytes

    :rtype: List[SimulationResult]
    """
    if connexion.request.is_json:
        logger.info("Start command")
        body = Simulation.from_dict(connexion.request.get_json())  # noqa: E501

        #gridId = getDataJSON(body, "gridId")
        #thresholdLow = getDataJSON(body, "thresholdLow")
        #thresholdMedium = getDataJSON(body, "thresholdMedium")
        #thresholdHigh = getDataJSON(body, "thresholdHigh")
        #logger.info("Id of the grid: " + str(gridId))
        #logger.info("Threshold low: " + str(thresholdLow))
        #logger.info("Threshold medium: " + str(thresholdMedium))
        #logger.info("Threshold high: " + str(thresholdHigh))
    return 'Response'

