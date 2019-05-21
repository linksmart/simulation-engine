import connexion
import six, logging, os, json
import pickle
import jsonpickle

from swagger_server.controllers.commands_controller import variable
from swagger_server.models.grid import Grid  # noqa: E501
from swagger_server import util

from swagger_server.controllers.utils import constant as c
from data_management.redisDB import RedisDB

from swagger_server.controllers.threadFactory import ThreadFactory
from data_management.utils import Utils

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
        logger.debug("Grid: " + str(grid)) #shows the raw data sent from client

        ####generates an id an makes a directory with the id for the data and for the registry
        try:
            id = utils.create_and_get_ID()
            redis_db = RedisDB()
            redis_db.set(id, "created")
            flag = redis_db.get(id)
            logger.debug("id stored in RedisDB: "+str(flag))
            #dir = os.path.join(os.getcwd(), "utils", str(id))
            #if not os.path.exists(dir):
                #os.makedirs(dir)
            #dir_data = os.path.join(os.getcwd(), "optimization", str(id), "mqtt")
            #if not os.path.exists(dir_data):
                #os.makedirs(dir_data)
        except Exception as e:
            logger.error(e)

        #logger.info("This is the Grid: " + str(grid))#Only for debugging purpose
        radial = grid.radials

        #logger.info("These are the radials: "+ str(radial))

        #linecodes = [c().linecodes[0]]
        #logger.debug("Linecode: "+str(linecodes))
        #gridController= gControl()
        factory= ThreadFactory(id)
        variable.set(id, factory)
        logger.debug("Factory instance stored")
        #redis_db.set("factory: "+id, json.dumps(factory))
        #logger.debug("Factory: "+str(factory[id]))
        #object=redis_db.get("factory: "+id)
        #logger.debug("Factory stored in redisDB: "+str(object))
        #test= json.loads(object[id])
        #logger.debug("Factory stored in redisDB: " + str(test)+" type: "+str(type(test)))
        factory.gridController.setNewCircuit(id)

        for values in radial:
            #logger.debug("values of the radial: "+str(values))
            values=values.to_dict()
            #logger.debug("Values: "+str(values))
            if "transformer" in values.keys() and values["transformer"] is not None:
                logger.debug("---------------Setting Transformers------------------------")
                transformer = values["transformer"]
                logger.debug("Transformers" + str(transformer))
                factory.gridController.setTransformers(id,transformer)
                
            if "loads" in values.keys() and values["loads"] is not None:
                logger.debug("---------------Setting Loads-------------------------")
                # radial=radial.to_dict()
                load = values["loads"]
                logger.debug("Loads" + str(transformer))
                factory.gridController.setLoads(id, load)

            if "power_lines" in values.keys() and values["power_lines"] is not None:
                logger.debug("---------------Setting Powerlines-------------------------")
                powerLines = values["power_lines"]
                #linecodes = values["linecode"]
                #factory.gridController.setPowerLines(id, powerLines, linecodes) #TODO: Where does linecodes come from?
                logger.debug("Powerlines" + str(powerLines))
                factory.gridController.setPowerLines(id, powerLines)

            if "powerProfile" in values.keys() and values["powerProfile"] is not None:
                powerProfile = values["powerProfile"]
                #logger.debug("Powerprofile" + str(powerProfile))
                factory.gridController.setPowerProfile(id, powerProfile)

            if "xycurves" in values.keys() and values["xycurves"] is not None:
                xycurves = values["xycurves"]#TORemove
                factory.gridController.setXYCurve(id, xycurves) 

            if "photovoltaics" in values.keys() and values["photovoltaics"] is not None:
                photovoltaics = values["photovoltaics"]
                xycurves = radial["xycurves"]
                loadshapes = radial["loadshapes"]
                tshapes = radial["tshapes"]
                factory.gridController.setPhotovoltaic(id, photovoltaics, xycurves, loadshapes, tshapes)

            """
            and "xycurves" in radial.values.keys()s() and radial["xycurves"] is not None 
                            and "loadshapes" in radial.values.keys()s() and radial["loadshapes"] is not None 
                            and "tshapes" in radial.values.keys()s() and radial["tshapes"] is not None: 
            """
            if "storage_units" in values.keys() and values["storage_units"] is not None:
                logger.debug("---------------Setting Storage-------------------------")
                # radial=radial.to_dict()
                storage = values["storage_units"]
                factory.gridController.setStorage(id, storage)
            """if "chargingPoints" in values.keys() and values["chargingPoints"] is not None:
                # radial=radial.to_dict()
                chargingPoints = values["chargingPoints"]
                gridController.setChargingPoints(id, chargingPoints)
            """
            if "chargingPoints" in values.keys() and values["chargingPoints"] is not None:
                chargingPoints = values["chargingPoints"]
                factory.gridController.setChargingPoints(id, chargingPoints)               
            if "linecode" in values.keys() and values["linecode"] is not None:
                logger.debug("---------------Setting LineCode-------------------------")
                linecode = values["linecode"]
                logger.debug("LineCode: " + str(linecode))
                factory.gridController.setLineCode(id, linecode)   
            if "capacitor" in values.keys() and values["capacitor"] is not None:
                logger.debug("---------------Setting Capacitors-------------------------")
                capacitor = values["capacitor"]
                #logger.debug("Capacitors: " + str(capacitor))
                factory.gridController.setCapacitors(id, capacitor) 
                
            if "voltage_regulator" in values.keys() and values["voltage_regulator"] is not None:
                logger.debug("---------------Setting Voltage regulator-------------------------")
                voltage_regulator = values["voltage_regulator"]
                logger.debug("Voltage Regulator: " + str(voltage_regulator))
                factory.gridController.setVoltageRegulator(id, voltage_regulator) 
            if "loadshapes" in values.keys() and values["loadshapes"] is not None:
                logger.debug("---------------Setting loadshapes-------------------------")
                loadshapes = values["loadshapes"]
                logger.debug("Load Shapes: " + str(loadshapes))
                factory.gridController.setLoadShape(id, loadshapes) 
            if "tshapes" in values.keys() and values["tshapes"] is not None:
                logger.debug("---------------Setting tshapes-------------------------")
                tshapes = values["tshapes"]
                logger.debug("Tshapes: " + str(tshapes))
                factory.gridController.setTShape(id, tshapes)                 
        ######Disables circuits untilo the run simulation is started
        #factory.gridController.disableCircuit(id)
        result = factory.gridController.run()
        #factory.gridController.run()
        #return str(result) 
        return id 
        #return " Result: " + str(result)
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
    try:
        f = open('/usr/src/app/tests/results/results.txt') #open(str(id)+"_results.txt")
        result = f.readlines()
        logger.debug(result)
        f.close()
    except:
        result = "None"
    return result

def delete_simulation(id):  # noqa: E501
    """Delete a simulation and its data

     # noqa: E501

    :param id: ID of the simulation
    :type id: str

    :rtype: None
    """
    return 'Simulation ' + id + ' deleted!'


def update_simulation(id, body):  # noqa: E501
    """Send new data to an existing simulation

     # noqa: E501

    :param id: ID of the simulation
    :type id: str
    :param radial: Updated grid data
    :type radial: dict | bytes

    :rtype: None
    """
    if connexion.request.is_json:
        body = Grid.from_dict(connexion.request.get_json())  # noqa: E501
    return 'Simulation ' + id + ' updated!'