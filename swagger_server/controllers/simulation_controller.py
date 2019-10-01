import sys

import connexion
import six, logging, os, json
import pickle
import jsonpickle

from swagger_server.controllers.commands_controller import variable
from swagger_server.models.grid import Grid  # noqa: E501
from swagger_server import util


from data_management.redisDB import RedisDB

from swagger_server.controllers.threadFactory import ThreadFactory
from data_management.utils import Utils


from profess.Profess import *
from profess.JSONparser import *
from profiles.profiles import *

logging.basicConfig(format='%(asctime)s %(levelname)s %(name)s: %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__file__)

utils = Utils()


def create_simulation(body):  # noqa: E501
    """Send grid data to simulation engine in order to create a new simulation

     # noqa: E501

    :param radial: Grid to be simulated
    :type radial: dict | bytes

    :rtype: str
    """
    if connexion.request.is_json:
        logger.debug("Post grid request")
        data = connexion.request.get_json()
        #temp = json.loads(json.dumps(data))
        #logger.debug("Data: " + str(temp)) #shows the raw data sent from client
        grid = Grid.from_dict(data)  # noqa: E501. SOMETHING IS NOT GOOD HERE
        #logger.debug("Grid: " + str(grid)) #shows the raw data sent from client
        id = utils.create_and_get_ID()
        redis_db = RedisDB()
        redis_db.set(id, "created")
        flag = redis_db.get(id)
        logger.debug("id stored in RedisDB: "+str(flag))
        redis_db.set("run:" + id, "created")

        radial = data["radials"]
        models_list = ["Maximize Self-Consumption", "Maximize Self-Production", "MinimizeCosts"]

        for values in radial:

            if "powerLines" in values.keys() and values["powerLines"] is not None:
                logger.debug("Checking Powerlines")

                powerLines = values["powerLines"]
                for power_lines_elements in powerLines:
                    if "r1" in power_lines_elements.keys() and "linecode" in power_lines_elements.keys():
                        message = "r1 and linecode cannot be entered at the same time in power line with id: " + str(
                            power_lines_elements["id"])
                        logger.error(message)
                        return message
            logger.debug("Power lines succesfully checked")

            if "powerProfile" in values.keys():
                logger.debug("Checking power profile IDs")
                load_profiles = values["loads"]
                load_profile_ids = []
                for load_profile in load_profiles:
                    load_profile_ids.append(load_profile['power_profile_id'])
                    
                power_profiles = values['powerProfile']
                for power_profile in power_profiles:
                    if power_profile['id'] not in load_profile_ids:
                        message = "Power profile IDs in loads and powerProfile do not match"
                        logger.error(message)
                        return message
                logger.debug("Power Profile IDs successfully checked")
                logger.debug("Checking for Interval values")
                for power_profile in power_profiles:
                    count_items = len(power_profile['items'])
                    if power_profile['interval']:
                        if count_items*power_profile['interval'] >= 24:
                            continue
                    elif power_profile['m_interval']:
                        if count_items * power_profile['m_interval'] >= 24*60:
                            continue
                    elif power_profile['s_interval']:
                        if count_items * power_profile['s_interval'] >= 24*3600:
                            continue
                    else:
                        message = "Error: The number of items in powerProfile should be according to the interval given"
                        return message
                logger.debug("Interval values successfully checked")

            data_to_store=[]
            if "storageUnits" in values.keys() and values["storageUnits"] is not None:
                logger.debug("Checking Storage")

                if not is_PV(radial):
                    message = "Error: no PV element defined for each storage element"
                    return message
                storage = values["storageUnits"]
                for storage_elements in storage:
                    # checking if default values are given
                    storage_eleement_change = storage_elements
                    if not "charge_efficiency" in storage_elements.keys():
                        storage_eleement_change["charge_efficiency"] = 90
                    if not "discharge_efficiency" in storage_elements.keys():
                        storage_eleement_change["discharge_efficiency"] = 90

                    data_to_store.append(storage_eleement_change)

                    #checking if there is a PV in the node of the ESS
                    if not storage_elements["optimization_model"] in models_list:
                        message = "Solely the following optimization models for storage control are possible: " + str(
                            models_list)
                        return message
                    bus_pv = get_PV_nodes(values["photovoltaics"])
                    if not storage_elements["bus1"] in bus_pv:
                        message = "Error: no PV element defined for storage element with id: " + str(
                            storage_elements["id"])
                        return message

            logger.debug("Storage successfully checked")

            data_to_store_cs = []
            if "chargingStations" in values.keys() and values["chargingStations"] is not None:
                logger.debug("Checking Charging stations")

                cs = values["chargingStations"]

                for cs_element in cs:
                    # checking if default values are given
                    cs_element_change = cs_element
                    if not "type_application" in cs_element.keys():
                        cs_element_change["type_application"] = "residential"

                    data_to_store_cs.append(cs_element_change)


                    # checking if there is a PV in the node of the ESS
                    bus_pv = get_PV_nodes(values["photovoltaics"])
                    bus_ess = get_ESS_nodes(values["storageUnits"])
                    if cs_element["bus"] in bus_ess:
                        if not cs_element["bus"] in bus_pv :
                            message = "Error: no PV element defined for charging station element with id: " + str(
                                cs_element["id"])
                            return message

            logger.debug("Charging stations successfully checked")

            #logger.debug("data to store "+str(data_to_store))

            data["radials"][0]["storageUnits"] = data_to_store
            data["radials"][0]["chargingStations"] = data_to_store_cs

        logger.debug("data"+str(data))
        #logger.debug("data" + str(data["radials"][0]["storageUnits"]))
        ####generates an id an makes a directory with the id for the data and for the registry
        try:

            dir_data = os.path.join("data",  str(id))

            if not os.path.exists(dir_data):
                os.makedirs(dir_data)

            fname = str(id)+"_input_grid"
            logger.debug("File name = " + str(fname))
            path = os.path.join("data",str(id), fname)
            utils.store_data(path, data)

        except Exception as e:
            logger.error(e)

        logger.debug("Grid data stored")
        return id
    else:
        return "Bad JSON Format"

def is_PV(radial):
    for values in radial:
        if "photovoltaics" in values:
            return True
        else:
            return False

def get_PV_nodes(list_pv):
    bus=[]
    for pv_element in list_pv:
        bus.append(pv_element["bus1"])
    return bus

def get_ESS_nodes(list_ess):
    bus=[]
    for ess_element in list_ess:
        bus.append(ess_element["bus1"])
    return bus

def get_simulation_result(id):  # noqa: E501
    """Get a simulation result

     # noqa: E501

    :param id: ID of the simulation
    :type id: str

    :rtype: Simulation result - array of nodes, and corresponding voltage
    """

    try:
        fname = str(id) + "_result"
        logger.debug("File name = " + str(fname))
        path = os.path.join("data", str(id), fname)
        result = utils.get_stored_data(path)

    except Exception as e:
        logger.error(e)
        result = e
    return result

def delete_simulation(id):  # noqa: E501
    """Delete a simulation and its data

     # noqa: E501

    :param id: ID of the simulation
    :type id: str

    :rtype: None
    """

    status = "None"
    try:
        import shutil
        folder_name = os.path.join("data", str(id))
        shutil.rmtree(folder_name)
        #util.rmfile(id, "data")
        status = 'Simulation ' + str(id) + ' deleted!'
    except:
        status = "ERROR: Could not delete Simulation " + str(id)
    return status

def mod_dict(data, k, v):
    for key in data.keys():
        if key == k:
            data[key] = v
        elif type(data[key]) is dict:
            mod_dict(data[key], k, v)
            
def update_simulation():  # noqa: E501 ##TODO: work in progress
    """Send new data to an existing simulation

     # noqa: E501

    :param id: ID of the simulation
    :type id: str
    :param radial: Updated grid data
    :type radial: dict | bytes

    :rtype: None
    """
    """if connexion.request.is_json:
        body = Grid.from_dict(connexion.request.get_json())  # noqa: E501
        logger.debug(body)"""
    fileid = connexion.request.args.get('id')
    key = connexion.request.args.get('key')
    value = connexion.request.args.get('value')
    try:
        dir_data = os.path.join("data", str(fileid))

        if not os.path.exists(dir_data):
            return "Id not existing"

        fname = str(fileid) + "_input_grid"
        logger.debug("File name = " + str(fname))
        path = os.path.join("data", str(fileid), fname)

        f = open(path, 'a') #open(str(id)+"_results.txt")
        #logger.debug("GET file "+str(f))
        content = f.read()
        #logger.info(content)
        data = json.loads(content)
        f.close()
        #utils.store_data(path, data)

        mod_dict(data, key, value)
    except:
        logger.debug("Error updating")
    return 'Simulation ' + fileid + ' updated!'
