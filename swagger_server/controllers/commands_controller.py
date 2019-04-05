import connexion
import six
import logging, time
#from flask import json
import pickle
import json
import jsonpickle


from swagger_server.models.simulation import Simulation  # noqa: E501
from swagger_server import util
from data_management.controller import gridController as gControl
from swagger_server.models.simulation_result import SimulationResult
from swagger_server.models.voltage import Voltage
from swagger_server.models.error import Error
from data_management.redisDB import RedisDB
from swagger_server.controllers.threadFactory import ThreadFactory

from  more_itertools import unique_everseen


logging.basicConfig(format='%(asctime)s %(levelname)s %(name)s: %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__file__)



class CommandController:

    def __init__(self):
        self.factory = {}
        self.redisDB=RedisDB()
        self.statusThread = {}
        self.running = {}

    def set_isRunning(self, id, bool):
        self.running[id] = bool

    def set(self, id, object):
        logger.debug("Object in set: "+str(object))
        try:
            self.factory[id] = object
        except Exception as e:
            logger.debug(e)

    def get(self, id):
        return self.factory[id]

    def isRunningExists(self):
        logger.debug("IsRunning exists: " + str(len(self.running)))
        if len(self.running):
            return True
        else:
            return False

    def get_isRunning(self, id):
        if id in self.running.keys():
            return self.running[id]
        else:
            return False

    def get_running(self):
        return self.running

    def get_statusThread(self, id):
        return self.statusThread[id]

    def run(self, id, json_object):
        logger.debug("Run in command controller started")
        self.id = id
        self.duration = json_object.duration
        logger.debug("Duration: "+str(self.duration))
        #gridController = gControl()
        #self.factory= jsonpickle.decode(self.redisDB.get("factory: "+id))
        #self.redisDB.get("factory: " + id)
        #logger.debug("This is the factory for command controller: "+str(self.factory))
        #self.set(self.id, self.redisDB.get("factory: " + id))
        #gridController.setParameters(id,)
        #logger.debug("Thread set")
        #
        try:
            self.redisDB.set("run:" + self.id, "running")
            logger.debug("Status: "+str(self.redisDB.get("run:" + self.id)))
            logger.debug("Thread: " + str(self.get(self.id)))
            listNames, listValues = self.get(self.id).startController(self.duration)
            self.redisDB.set("run:" + self.id, "stop")
            return buildAnswer(listNames, listValues, json_object.threshold_high, json_object.threshold_medium,
                               json_object.threshold_low)

        except Exception as e:
            logger.error(e)
            return e
        #self.set_isRunning(self.id, True)
        #logger.debug("Flag isRunning set to True")
        #logger.info("running status " + str(self.running))

        #logger.info("running status " + str(self.redisDB.get("run:" + self.id)))
        #logger.debug("from redis: "+str(self.factory)+" type: "+str(type(self.factory)))
        #self.factory=ThreadFactory()
        #logger.debug("Normal: " + str(self.factory) + " type: " + str(type(self.factory)))
        #listNames, listValues = self.factory.startController()

        #return "started"
        #return (listNames, listValues)
        #return buildAnswer(listNames, listValues, json_object.threshold_high, json_object.threshold_medium, json_object.threshold_low)

    def abort(self, id):
        logger.debug("Abort signal received")
        logger.debug("This is the factory object: " + str(self.get(id)))
        if self.factory[id]:
            self.factory[id].stopControllerThread()
            self.set_isRunning(id, False)
            message = "System stopped succesfully"
            logger.debug(message)
        else:
            message = "No threads found"
            logger.debug(message)

    def run_status(self, id):
        while True:
            status = self.get(id).is_running()
            flag = self.redisDB.get("run:" + id)
            logger.debug("Control run_status: "+str(flag))
            if not status or (flag is not None and flag == "stop"):
                logger.debug("Control run_status: "+str(flag))
                self.redisDB.remove("run:" + id)
                self.stop(id)
                break
            time.sleep(1)

variable = CommandController()

def abort_simulation(id):  # noqa: E501
    """Aborts a running simulation

    If the user of the professional GUI decides to abort a running simulation this call will be triggered # noqa: E501


    :rtype: None
    """

    try:
        redis_db = RedisDB()
        flag = redis_db.get("run:" + id)
        message = ""
        if flag is not None and flag == "running":
            logger.debug("System running and trying to stop")
            redis_db.set("run:" + id, "stop")
            time.sleep(1)
            flag = redis_db.get("run:" + id)
            if flag is None:
                logger.debug("System stopped succesfully")
                message = "System stopped succesfully"
        elif flag is None:
            logger.debug("System already stopped")
            message = "System already stopped"
    except Exception as e:
        logger.error(e)
        message = "Error stoping the system"
    return message


def run_simulation(id, body):  # noqa: E501
    """Runs a simulation

     # noqa: E501

    :param body: Run a simulation
    :type body: dict | bytes

    :rtype: List[SimulationResult]
    """
    if connexion.request.is_json:
        logger.info("Start command")
        body = Simulation.from_dict(connexion.request.get_json())  # noqa: E501

        try:
            redis_db = RedisDB()
            flag = redis_db.get(id)
            if flag is not None and flag == "created":
                if variable.isRunningExists():
                    logger.debug("isRunning exists")
                    if not variable.get_isRunning(id):
                        response = variable.run(id, body)
                        return response
                    else:
                        logger.debug("System already running")
                        return "System already running"
                else:
                    logger.debug("isRunning not created yet")
                    response = variable.run(id, body)
                    return response
            else:
                response = "Id not existing"

        except Exception as e:
            logger.debug("e")
            response = e

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