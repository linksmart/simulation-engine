import connexion
import six
import logging
from flask import json

from swagger_server.models.simulation import Simulation  # noqa: E501
from swagger_server import util
from data_management.controller import gridController as gControl
from swagger_server.models.simulation_result import SimulationResult
from swagger_server.models.voltage import Voltage
from swagger_server.models.error import Error

from  more_itertools import unique_everseen


logging.basicConfig(format='%(asctime)s %(levelname)s %(name)s: %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__file__)


def abort_simulation():  # noqa: E501
    """Aborts a running simulation

    If the user of the professional GUI decides to abort a running simulation this call will be triggered # noqa: E501


    :rtype: None
    """
    return 'do some magic!'


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
        listNames, listValues = gridController.runSimulation(body.grid_id,body.duration)
        response = buildAnswer(listNames,listValues,body.threshold_high,body.threshold_medium,body.threshold_low)
    return response


def buildAnswer(listNames=None, listValues=None, thres_High = 0.1, thres_Medium=0.05, thres_Low=0.025):

    body = []
    values = []
    names = []
    values_error=[]


    for name in listNames:
        names.append(name.split('.',1)[0])
        names=list(unique_everseen(names))

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


        errors=checkError(group_value, thres_High, thres_Medium, thres_Low)
        values_error.append(errors)
        voltages=Voltage(group_value[0],group_value[1],group_value[2])
        values.append(voltages)
        #del group_value[:]
        group_value = [None] * 3

    for i in range(len(names)):
        body.append(SimulationResult(names[i], values[i],values_error[i]))

    return body

def checkError(value, thresHigh, thresMedium, thresLow):
    group_value_error_high = [None] * 3
    group_value_error_medium = [None] * 3
    group_value_error_low = [None] * 3

    counter = 0
    for val in value:
        logger.info("Counter: " + str(counter))
        if val != None:
            logger.info("Val: "+ str(val))
            if float(val) < (1 - thresHigh) or float(val) > (1 + thresHigh):
                group_value_error_high[counter] = val
            elif (float(val) < (1 - thresMedium) or float(val) > (1 + thresMedium)):
                group_value_error_medium[counter] = val
            elif (float(val) < (1 - thresLow) or float(val) > (1 + thresLow)):
                group_value_error_low[counter] = val

            counter = counter + 1
        else:
            counter = counter + 1

    error=Error(group_value_error_high,group_value_error_medium,group_value_error_low)
    return error