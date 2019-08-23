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
        #----------Profiles---------------#

        #pv_profile_data = prof.pv_profile("bolzano", "italy", days=365)
        #print("pv_profile_data: " + str(pv_profile_data))
        #load_profile_data = prof.load_profile(type="residential", randint=5, days=365)
        #print("load_profile_data: " + str(load_profile_data))
        #t_end = time.time() + 60
        #days = 1
        #while time.time() < t_end:
        #    prof.price_profile("fur", "denmark", days)
        #   days = days + 1
        #   time.sleep(5)

        #----------Profiles_end-----------#



        ####generates an id an makes a directory with the id for the data and for the registry
        try:
            #dir = os.path.join(os.getcwd(), "utils", str(id))
            #if not os.path.exists(dir):
                #os.makedirs(dir)
            dir_data = os.path.join("data",  str(id))

            if not os.path.exists(dir_data):
                os.makedirs(dir_data)
            #if not os.path.exists("data"+str(id)):
                #os.makedirs("data"+str(id))


            #os.chdir(r"./data")
            fname = str(id)+"_input_grid"
            logger.debug("File name = " + str(fname))
            path = os.path.join("data",str(id), fname)
            utils.store_data(path, data)
            #f = open(fname,'w')
            #json.dump(data, f, ensure_ascii=False, indent=2)
            #f.close()
            #os.chdir(r"../")
        except Exception as e:
            logger.error(e)

        logger.debug("Grid data stored")

        radial = data["radials"]
        models_list = ["Maximize Self-Consumption", "Maximize Self-Production", "MinimizeCosts"]

        for values in radial:
            #logger.debug("values of the radial: "+str(values))
            #for key in values.keys():
                #logger.debug("keys of the radial: " + str(key))

            if "storageUnits" in values.keys() and values["storageUnits"] is not None:
                # logger.debug("---------------Setting Storage-------------------------")
                logger.debug("! ---------------Setting Storage------------------------- \n")
                # radial=radial.to_dict()
                storage = values["storageUnits"]
                for storage_elements in storage:
                    if not storage_elements["optimization_model"] in models_list:
                        message = "Following optimization models are possible: " + str(models_list)
                        return message
        return id
    else:
        return "Bad JSON Format"
    
def get_simulation_result(id):  # noqa: E501
    """Get a simulation result

     # noqa: E501

    :param id: ID of the simulation
    :type id: str

    :rtype: Simulation result - array of nodes, and corresponding voltage
    """
    #factory= ThreadFactory(id)
    #variable.set(id, factory)
    #result = factory.gridController.results()
    #logger.info("Get Error")
    try:
        fname = str(id) + "_result"
        logger.debug("File name = " + str(fname))
        path = os.path.join("data", str(id), fname)
        result = utils.get_stored_data(path)


        """os.chdir(r"./data")
        f = open(str(id)+"_result") #open(str(id)+"_results.txt")
        #logger.debug("GET file "+str(f))
        content = f.read()
        #logger.info(content)
        result = json.loads(content)
        f.close()
        os.chdir(r"../")"""
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
    """factory= ThreadFactory(id)
    try:
        factory.gridController.disableCircuit(id)
        status = 'Simulation ' + id + ' deleted!'
    except:
        status = "Could not delete Simulation " + id
    return status"""
    status = "None"
    try:
        util.rmfile(id, "data")
        status = 'Simulation ' + id + ' deleted!'
    except:
        status = "Could not delete Simulation " + id
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
        os.chdir(r"./data")
        f = open(fileid+"_input_grid", 'a') #open(str(id)+"_results.txt")
        #logger.debug("GET file "+str(f))
        content = f.read()
        #logger.info(content)
        data = json.loads(content)
        f.close()
        os.chdir(r"../")
        #key = body[0]
        #value = 
        mod_dict(data, key, value)
    except:
        logger.debug("Error updating")
    return 'Simulation ' + fileid + ' updated!'
