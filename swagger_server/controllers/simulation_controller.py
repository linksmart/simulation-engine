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
        body = Grid.from_dict(connexion.request.get_json())  # noqa: E501
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

            if "powerLines" in values.keys():
                if values["powerLines"] is not None:
                    logger.debug("Checking Powerlines")

                    powerLines = values["powerLines"]
                    for power_lines_elements in powerLines:
                        if "r1" in power_lines_elements.keys() and "linecode" in power_lines_elements.keys():
                            message = "r1 and linecode cannot be entered at the same time in power line with id: " + str(
                                power_lines_elements["id"])
                            logger.error(message)
                            return message, 406
            logger.debug("Power lines succesfully checked")

            if "powerProfile" in values.keys():
                if values["powerProfile"] is not None:
                    logger.debug("Checking power profile IDs")
                    load_profiles = values["loads"]
                    load_profile_ids = []
                    for load_profile in load_profiles:
                        if "power_profile_id" in load_profile.keys() and load_profile['power_profile_id'] is not None:
                            load_profile_ids.append(load_profile['power_profile_id'])

                    power_profile_ids = []
                    power_profiles = values['powerProfile']
                    for power_profile in power_profiles:
                        if "id" in power_profile.keys() and power_profile['id'] is not None:
                            power_profile_ids.append(power_profile['id'])

                    for load_profile_id in  load_profile_ids:
                        if not bool(re.search("profile_\d", load_profile_id)):
                            if load_profile_id not in power_profile_ids:
                                message = "Error: No Power profile found for this ID: " + str(load_profile_id)
                                logger.error(message)
                                return message, 406

                    logger.debug("Power Profile IDs successfully checked")
                    logger.debug("Checking Interval values")
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
                        message = "Error: The number of items in powerProfile should be according to the interval given"
                        return message, 406
                    logger.debug("Interval values successfully checked")

            data_to_store=[]

            if "storageUnits" in values.keys():
                if values["storageUnits"] is not None:
                    logger.debug("Checking Storage")

                    if not is_PV(radial):
                        message = "Error: no PV element defined for each storage element"
                        return message
                    storage = values["storageUnits"]
                    bus_pv = get_PV_nodes(values["photovoltaics"])
                    logger.debug("bus pv "+str(bus_pv))
                    bus_load = get_Load_nodes(values["loads"])
                    logger.debug("bus loads " + str(bus_load))
                    bus_ess = get_ESS_nodes(storage)
                    logger.debug("bus ess " + str(bus_ess))
                    for element in bus_ess:
                        if not element in bus_pv:
                            message = "Error: no PV element or wrong bus definition of PV element for storage element with bus: " + str(
                                element)
                            return message, 406
                        if not element in bus_load:
                            message = "Error: no Load element or wrong bus definition of Load element for storage element with bus: " + str(
                                element)
                            return message, 406


                    for storage_elements in storage:
                        # checking if default values are given
                        storage_eleement_change = storage_elements
                        if not "charge_efficiency" in storage_elements.keys():
                            storage_eleement_change["charge_efficiency"] = 90
                        if not "discharge_efficiency" in storage_elements.keys():
                            storage_eleement_change["discharge_efficiency"] = 90
                        if not "global_control" in storage_elements.keys():
                            storage_eleement_change["global_control"] = False

                        data_to_store.append(storage_eleement_change)

                        #checking if there is a PV in the node of the ESS
                        if not storage_elements["optimization_model"] in models_list:
                            message = "Solely the following optimization models for storage control are possible: " + str(
                                models_list)
                            return message, 406

                        """if "." in storage_elements["bus1"]:
                            message = "Error: storage element with id: " + str(
                                storage_elements["id"] +" is not three-phase")
                            return message"""


            logger.debug("Storage successfully checked")

            data_to_store_cs = []
            if "chargingStations" in values.keys():
                if values["chargingStations"] is not None:
                    logger.debug("Checking Charging stations")

                    cs = values["chargingStations"]
                    if is_PV(radial):
                        bus_pv = get_PV_nodes(values["photovoltaics"])
                        logger.debug("bus_pv_cs " + str(bus_pv))
                    if is_ESS(radial):
                        bus_ess = get_ESS_nodes(values["storageUnits"])
                        logger.debug("bus_ess_cs " + str(bus_ess))

                    for cs_element in cs:
                        # checking if default values are given
                        cs_element_change = cs_element
                        if not "type_application" in cs_element.keys():
                            cs_element_change["type_application"] = "residential"

                        data_to_store_cs.append(cs_element_change)


                        # checking if there is ESS with charging station. If one present then PV should be present
                        if is_ESS(radial):
                            logger.debug("cs_bus "+str([cs_element["bus"]]))
                            cs_bus = cs_element["bus"]
                            if "." in cs_bus:
                                if [cs_bus.split(".")[0]] in bus_ess:
                                    if not [cs_bus] in bus_ess:
                                        message = "Error: wrong bus definition for charging station element with bus: " + str(
                                            cs_bus)
                                        return message, 406
                                    else:
                                        if not [cs_element["bus"]] in bus_pv:
                                            message = "Error: no aggreement in bus definition for PV element, Storage element and charging station element with bus: " + str(
                                                cs_bus)
                                            return message, 406
                            elif [cs_bus] in bus_ess:
                                if not [cs_element["bus"]] in bus_pv :
                                    message = "Error: no aggreement in bus definition for PV element, Storage element and charging station element with bus: " + str(
                                        cs_bus)
                                    return message, 406


                    bus_cs = get_charging_station_nodes(data_to_store_cs)
                    logger.debug("bus_cs "+str(bus_cs))
                    for cs_element in data_to_store_cs:
                        logger.debug("cs_element "+str(cs_element))
                        # checking if there is just one residential
                        #if cs_element["type_application"] == "residential":"""


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

def is_ESS(radial):
    for values in radial:
        if "storageUnits" in values:
            return True
        else:
            return False

def get_PV_nodes(list_pv):
    bus=[]
    for pv_element in list_pv:
        bus_name = pv_element["bus1"]
        bus.append(bus_name)

    bus_to_send = order_nodes_in_lists(bus)
    return bus_to_send

def get_charging_station_nodes(list_cs):
    bus = []
    for cs_element in list_cs:
        bus_name = cs_element["bus"]
        bus.append(bus_name)

    bus_to_send = order_nodes_in_lists(bus)
    return bus_to_send

def order_nodes_in_lists(list_nodes):
    bus_to_send = []
    substring_list = [".1", ".2", ".3"]
    for bus_name_2 in list_nodes:
        if "." in bus_name_2:
            name_root = bus_name_2.split(".")[0]
            bus_name_list = [idx for idx in list_nodes if idx.split(".")[0] == name_root]
            flag = True
            for substring in substring_list:
                flag_temp = False
                for element in bus_name_list:
                    if substring in element:
                        flag_temp = True
                flag = flag and flag_temp
            if flag:
                bus_to_send.append([name_root])
            else:
                bus_to_send.append(bus_name_list)
        else:
            bus_to_send.append([bus_name_2])

    if not bus_to_send == []:
        import itertools
        bus_to_send = list(k for k, _ in itertools.groupby(bus_to_send))

    return bus_to_send

def get_ESS_nodes(list_ess):
    bus=[]
    for ess_element in list_ess:
        bus_name = ess_element["bus1"]
        bus.append(bus_name)

    bus_to_send = order_nodes_in_lists(bus)
    return bus_to_send

def get_Load_nodes(list_loads):
    bus = []
    for load_element in list_loads:
        bus_name = load_element["bus"]
        bus.append(bus_name)

    bus_to_send = order_nodes_in_lists(bus)
    return bus_to_send

"""def get_ESS_nodes(list_ess):
    bus=[]
    for ess_element in list_ess:
        bus.append(ess_element["bus1"])
    return bus"""

def get_simulation_result(id):  # noqa: E501
    """Get a simulation result

     # noqa: E501

    :param id: ID of the simulation
    :type id: str

    :rtype: Simulation result - array of nodes, and corresponding voltage
    """

    try:
        fname = str(id) + "_input_grid"
        logger.debug("File name = " + str(fname))
        path = os.path.join("data", str(id), fname)
        result = utils.get_stored_data(path)

    except Exception as e:
        logger.error(e)
        result = e
    return result

def get_simulation_result_raw_with_node(id, result_type, node_name):  # noqa: E501
    """Get a simulation result from result_raw file
    :param id: ID of the simulation :type str
    :param result_type: Result type such as voltages/currents/losses :type str
    :param node_name: Name of node/bus :type str

    :rtype: Simulation result - list of simulation results for the given result_type and node.
    """

    try:
        fname = str(id) + "_result_raw.json"
        logger.debug("File name = " + str(fname))
        path = os.path.join("data", str(id), fname)
        raw_data = utils.get_stored_data(path)
        print("Hello")
        output = []
        if(result_type in raw_data.keys() and raw_data[result_type] is not None):
            raw_data = raw_data[result_type]
            raw_data_keys = raw_data.keys()
            node_name = node_name + "."
            for key in raw_data_keys:
                if bool(re.search(node_name, key)):
                    if(result_type == "voltages"):
                        output.append(raw_data[key]['Voltage'])
                    else:
                        output.append(raw_data[key])
    except Exception as e:
        logger.error(e)
        output = e
    return output

def get_simulation_result_raw(id, result_type):  # noqa: E501
    """Get a simulation result from result_raw file
    :param id: ID of the simulation :type str
    :param result_type: Result type such as voltages/currents/losses :type str

    :rtype: Simulation result - list of simulation results for the given result_type.
    """

    try:
        fname = str(id) + "_result_raw.json"
        logger.debug("File name = " + str(fname))
        path = os.path.join("data", str(id), fname)
        raw_data = utils.get_stored_data(path)
        print("Hello")
        output = []
        if(result_type in raw_data.keys() and raw_data[result_type] is not None):
            output = raw_data[result_type]
    except Exception as e:
        logger.error(e)
        output = e
    return output

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
            
def update_simulation(id):  # noqa: E501 ##TODO: work in progress
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
    # fileid = connexion.request.args.get('id')
    fileid = id
    key = connexion.request.get_json().get('key')
    value = connexion.request.get_json().get('value')
    try:
        dir_data = os.path.join("data", str(fileid))

        if not os.path.exists(dir_data):
            return "Id not existing"

        fname = str(fileid) + "_input_grid"
        logger.debug("File name = " + str(fname))
        path = os.path.join("data", str(fileid), fname)

        # f = open(path, 'a') #open(str(id)+"_results.txt")
        with open(path, 'r') as f:
            content = f.read()
        #logger.debug("GET file "+str(f))
        # content = f.read()
        #logger.info(content)
        data = json.loads(content)
        # f.close()
        #utils.store_data(path, data)

        mod_dict(data, key, value)
        with open(path, 'w') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except:
        logger.debug("Error updating")
    return 'Simulation ' + fileid + ' updated!'
