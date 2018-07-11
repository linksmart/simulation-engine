import connexion
import six
import logging
from flask import json

from swagger_server.models.simulation import Simulation  # noqa: E501
from swagger_server.models.simulation_result import SimulationResult  # noqa: E501
from swagger_server import util
from data_management.controller import gridController as gControl
from swagger_server.models.simulation_result import SimulationResult
from swagger_server.models.voltage import Voltage

from  more_itertools import unique_everseen


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
        gridController = gControl()
        listNames, listValues = gridController.runSimulation(body.grid_id,body.duration,body.threshold_high,body.threshold_medium,body.threshold_low)
        response = buildAnswer(listNames,listValues)
    return response


def buildAnswer(listNames=None, listValues=None):

    body = []
    values = []
    names = []


    for name in listNames:
        names.append(name.split('.',1)[0])
        names=list(unique_everseen(names))

    logger.info("Names: "+str(names))

    group_value = [None] * 3
    for j in range(len(names)):
        for i in range(len(listValues)):
            if names[j] in listNames[i]:
                if ".1"  in listNames[i]:
                    group_value[0]=listValues[i]
                elif ".2"  in listNames[i]:
                    group_value[1] = listValues[i]
                elif ".3"  in listNames[i]:
                    group_value[2] = listValues[i]

        voltages=Voltage(group_value[0],group_value[1],group_value[2])
        #logger.info("Voltages: "+str(voltages))
        values.append(voltages)
        #del group_value[:]
        group_value = [None] * 3


    for i in range(len(names)):
        body.append(SimulationResult(names[i], str(values[i])))

    return body