import connexion
import six
import logging
import time
#from flask import json
import pickle
import json
import os
import threading
import data_management.redisDB


from swagger_server.models.simulation import Simulation  # noqa: E501
from swagger_server import util
from data_management.controller import gridController as gControl
from swagger_server.models.simulation_result import SimulationResult
from swagger_server.models.voltage import Voltage
from swagger_server.models.error import Error
from data_management.redisDB import RedisDB
from data_management.utils import Utils
from data_management.ModelException import InvalidModelException, MissingKeysException
from swagger_server.controllers.threadFactory import ThreadFactory

from more_itertools import unique_everseen


logging.basicConfig(
    format='%(asctime)s %(levelname)s %(name)s: %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__file__)


class CommandController:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if CommandController._instance is None:
            with CommandController._lock:
                if CommandController._instance is None:
                    CommandController._instance = super(
                        CommandController, cls).__new__(cls)
        return CommandController._instance

    def __init__(self):
        self.factory = {}
        self.redisDB = RedisDB()
        self.statusThread = {}
        self.running = {}
        self.utils = Utils()

    def set_isRunning(self, id, bool):
        self.running[id] = bool

    def set(self, id, object):
        logger.debug("Object in set: "+str(object))
        try:
            self.factory[id] = object
            # fname="factory_"+str(id)
            #path = os.path.join("data", fname)
            #self.utils.store_data(path, object)
        except Exception as e:
            logger.debug(e)

    def get(self, id):
        return self.factory[id]
        #fname= "factory_"+str(id)
        #path = os.path.join("data", fname)
        # return self.utils.get_stored_data(path)

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
        self.duration = json_object["sim_duration_in_hours"]
        logger.debug("Duration: "+str(self.duration))
        self.redisDB.set("timestep_" + str(id), str(0))
        self.redisDB.set("sim_days_" + str(id), str(self.duration))

        #gridController = gControl()
        #self.factory= jsonpickle.decode(self.redisDB.get("factory: "+id))
        #self.redisDB.get("factory: " + id)
        #logger.debug("This is the factory for command controller: "+str(self.factory))
        #self.set(self.id, self.redisDB.get("factory: " + id))
        # gridController.setParameters(id,)
        #logger.debug("Thread set")
        #
        try:

            self.set(self.id, ThreadFactory(self.id, self.duration))
            logger.debug("Factory instance stored")

            # redis_db.set("factory: "+id, json.dumps(factory))
            # logger.debug("Factory: "+str(factory[id]))
            # object=redis_db.get("factory: "+id)
            # logger.debug("Factory stored in redisDB: "+str(object))
            # test= json.loads(object[id])
            # logger.debug("Factory stored in redisDB: " + str(test)+" type: "+str(type(test)))
            #self.redisDB.set("run:" + self.id, "running")
            self.redisDB.set("run:" + id, "starting")
            logger.debug("Status: "+str(self.redisDB.get("run:" + self.id)))
            logger.debug("Thread: " + str(self.get(self.id)))
            msg = self.get(self.id).startController()
            logger.debug("Answer from Thread factory: " + str(msg))
            if msg == 0:
                self.set_isRunning(id, True)
                logger.debug("Flag isRunning set to True")
                self.statusThread[id] = threading.Thread(
                    target=self.run_status, args=(id,))
                logger.debug("Status of the Thread started")
                self.statusThread[id].start()
                meta_data = {"id": id,
                             "ztarttime": time.time()}
                self.redisDB.set("run:" + id, "running")
                self.redisDB.set("id_meta:" + id, json.dumps(meta_data))
                logger.info("running status " + str(self.running))
                logger.debug("Command controller start finished")
                return 0
            else:
                self.set_isRunning(id, False)
                logger.debug("Flag isRunning set to False")
                self.redisDB.set("run:" + id, "stopped")
                logger.error("Command controller start could not be finished")
                return 1
            #self.redisDB.set("run:" + self.id, "stop")
            # return buildAnswer(listNames, listValues, json_object.threshold_high, json_object.threshold_medium,
            #                  json_object.threshold_low)

        except Exception as e:
            logger.error(e)
            return e
        #self.set_isRunning(self.id, True)
        #logger.debug("Flag isRunning set to True")
        #logger.info("running status " + str(self.running))

        #logger.info("running status " + str(self.redisDB.get("run:" + self.id)))
        #logger.debug("from redis: "+str(self.factory)+" type: "+str(type(self.factory)))
        # self.factory=ThreadFactory()
        #logger.debug("Normal: " + str(self.factory) + " type: " + str(type(self.factory)))
        #listNames, listValues = self.factory.startController()

        # return "started"
        # return (listNames, listValues)
        # return buildAnswer(listNames, listValues, json_object.threshold_high, json_object.threshold_medium, json_object.threshold_low)

    def abort(self, id):
        logger.debug("Abort signal received")
        logger.debug("This is the factory object: " + str(self.get(id)))
        if self.factory[id]:
            self.factory[id].stopControllerThread()
            self.set_isRunning(id, False)
            message = "System stopped succesfully"
            self.redisDB.set("run:" + id, "stopped")
            logger.debug(message)
        else:
            message = "No threads found"
            logger.debug(message)

    def run_status(self, id):
        while True:
            status = self.get(id).is_running()
            flag = self.redisDB.get("run:" + id)
            logger.debug("Control run_status: "+str(flag))
            #logger.debug("status " + str(status))
            if status == "True" or (flag is not None and flag == "stop"):
                logger.debug("Control run_status: "+str(flag))
                self.redisDB.set("run:" + id, "stopping")
                self.abort(id)
                break
            time.sleep(2)


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
            logger.debug("Flag in stop: " + str(flag))

            if flag is None:
                logger.debug("System stopped succesfully")
                message = "System stopped succesfully"
            elif "stopping" in flag:
                message = "System stopped succesfully"
                counter = 0
                while ("stopping" in flag):
                    flag = redis_db.get("run:" + id)
                    counter = counter + 1
                    if counter >= 15:
                        message = "system stopped succesfully"
                        break
                    else:
                        time.sleep(1)
                logger.debug("System stopped succesfully")
            elif "stopped" in flag:
                logger.debug("System stopped succesfully")
                message = "System stopped succesfully"
            else:
                message = "Problems while stopping the system"
        elif flag is not None and flag == "stopped":
            logger.debug("System already stopped")
            message = "System already stopped"
        elif flag is None:
            logger.debug("System already stopped")
            message = "System already stopped"
    except Exception as e:
        logger.error(e)
        message = "Error stoping the system"
    return message


def get_simulation_status(id):  # noqa: E501
    """Get the status of the simulation

     # noqa: E501

    :param id: ID of the simulation
    :type id: str

    :rtype: float
    """
    try:
        dir = os.path.join("data", str(id))
        if not os.path.exists(dir):
            return "Id not existing"
        redis_db = RedisDB()
        flag = redis_db.get("run:" + id)
        logger.info("flag: " + str(flag))
        if flag == None or flag == "created":
            return "Simulation has not been started"
        logger.debug("#############Getting status#####################")
        status_message = redis_db.get("status_"+ str(id))
        if status_message == "OK":
            timestep = int(redis_db.get("timestep_"+str(id)))
            logger.debug("timestep "+str(timestep))
            sim_days = int(redis_db.get("sim_days_"+str(id)))
            logger.debug("sim_days "+str(sim_days))

            status = (timestep / (sim_days-1)) * 100.0

            if timestep == (sim_days - 1):
                flag_stop = redis_db.get("opt_stop_" + id)
                logger.debug("flag stop "+str(flag_stop))
                if flag_stop == "False":
                    status = status - 1
            return int(status)
        else:
            return status_message, 406

    except Exception as e:
        logger.error(e)
        status = "id not present"



def run_simulation(id, body=None):  # noqa: E501
    """Runs a simulation

    Runs a simulation # noqa: E501

    :param id: ID of the simulation that should be started
    :type id: str
    :param body: Configuration data for the simulation e.g. duration
    :type body: dict | bytes

    :rtype: List[SimulationResult]
    """
    logger.info("Running Simulation ...")
    if connexion.request.is_json:
        logger.info("Start command for simulation ID: " + id)
        data = connexion.request.get_json()
        logger.debug("data "+str(data)+" type "+str(type(data)))

        dir = os.path.join("data", str(id))
        if not os.path.exists(dir):
            return "Id not existing"

        redisDB = RedisDB()
        # flag = redis_db.get(id)
        flag = redisDB.get("run:" + id)
        logger.info("flag: " + str(flag))
        if flag is not None and flag == "running":
            return "System already running"
        else:
            try:
                # start random values for the status to become zero

                msg = variable.run(id, data)
                if msg == 0:
                    msg_to_send = "System started succesfully"
                else:
                    msg_to_send = "System could not start"
                return msg_to_send
            except (InvalidModelException, MissingKeysException) as e:
                logger.error("Error " + str(e))
                redisDB.set("run:" + id, "stopped")
                return str(e)

    else:
        logger.error("Wrong Content-Type")
        return "Wrong Content-Type"
        """if flag is not None and flag == "created":
                if variable.isRunningExists():
                    logger.debug("isRunning exists")
                    if not variable.get_isRunning(id):
                        response = variable.run(id, data)
                        return response
                    else:
                        logger.debug("System already running")
                        return "System already running"
                else:
                    logger.debug("isRunning not created yet")
                    response = variable.run(id, data)
                    return response
            else:
                response = "Id not existing"

        except Exception as e:
            logger.error(e)
            response = e

    return response"""


def buildAnswer(listNames=None, listValues=None, thres_High=0.1, thres_Medium=0.05, thres_Low=0.025):

    body = []
    values = []
    names = []
    values_error = []

    for name in listNames:
        names.append(name.split('.', 1)[0])
        names = list(unique_everseen(names))

    group_value = [None] * 3
    for j in range(len(names)):
        for i in range(len(listValues)):
            if names[j] in listNames[i]:
                if ".1" in listNames[i]:
                    group_value[0] = listValues[i]
                elif ".2" in listNames[i]:
                    group_value[1] = listValues[i]
                elif ".3" in listNames[i]:
                    group_value[2] = listValues[i]

        errors = checkError(group_value, thres_High, thres_Medium, thres_Low)
        values_error.append(errors)
        voltages = Voltage(group_value[0], group_value[1], group_value[2])
        values.append(voltages)
        #del group_value[:]
        group_value = [None] * 3

    for i in range(len(names)):
        body.append(SimulationResult(names[i], values[i], values_error[i]))

    return body


def checkError(value, thresHigh, thresMedium, thresLow):
    group_value_error_high = [None] * 3
    group_value_error_medium = [None] * 3
    group_value_error_low = [None] * 3

    counter = 0
    for val in value:
        logger.info("Counter: " + str(counter))
        if val != None:
            logger.info("Val: " + str(val))
            if float(val) < (1 - thresHigh) or float(val) > (1 + thresHigh):
                group_value_error_high[counter] = val
            elif (float(val) < (1 - thresMedium) or float(val) > (1 + thresMedium)):
                group_value_error_medium[counter] = val
            elif (float(val) < (1 - thresLow) or float(val) > (1 + thresLow)):
                group_value_error_low[counter] = val

            counter = counter + 1
        else:
            counter = counter + 1

    error = Error(group_value_error_high,
                  group_value_error_medium, group_value_error_low)
    return error
