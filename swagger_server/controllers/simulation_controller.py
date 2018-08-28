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


xycurves=[

    {
        "id":"panel_temp_eff",
        "npts":4,
        "xarray":[
            0,
            25,
            75,
            100
        ],
        "yarray":[
            1.2,
            1.0,
            0.8,
            0.6
        ]
    },
    {
        "id":"panel_absorb_eff",
        "npts":4,
        "xarray":[
            0.1,
            0.2,
            0.4,
            1.0
        ],
        "yarray":[
            0.86,
            0.9,
            0.93,
            0.97
        ]
    }

]

loadshapes = [

    {
        "id":"assumed_irrad",
        "npts":24,
        "interval":1,
        "mult":[
            0,
            0,
            0,
            0,
            0,
            0,
            0.1,
            0.2,
            0.3,
            0.5,
            0.8,
            0.9,
            1.0,
            1.0,
            0.99,
            0.9,
            0.7,
            0.4,
            0.1,
            0,
            0,
            0,
            0,
            0
        ]
    }

]

tshapes = [

    {
        "id":"assumed_Temp",
        "npts":24,
        "interval":1,
        "mult":[
            10,
            10,
            10,
            10,
            10,
            10,
            12,
            15,
            20,
            25,
            30,
            30,
            32,
            32,
            30,
            28,
            27,
            26,
            25,
            20,
            18,
            15,
            13,
            12
        ]
    }

]

def create_simulation(body):  # noqa: E501
    """Send grid data to simulation engine in order to create a new simulation

     # noqa: E501

    :param radial: Grid to be simulated
    :type radial: dict | bytes

    :rtype: str
    """
    if connexion.request.is_json:
        logger.debug("Post grid request")
        grid = Grid.from_dict(connexion.request.get_json())  # noqa: E501

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

        logger.info("This is the dictionary: " + str(grid))
        radial = grid.radials
        logger.info("These are the radials: "+ str(radial))


        linecodes = [c().linecodes[0]]
        logger.debug("Linecode: "+str(linecodes))
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
            logger.debug("values of the radial: "+str(values))
            values=values.to_dict()
            if "loads" in values.keys() and values["loads"] is not None:
                # radial=radial.to_dict()
                load = values["loads"]
                factory.gridController.setLoads(id, load)
            if "transformer" in values.keys() and values["transformer"] is not None:
                transformer = values["transformer"]
                factory.gridController.setTransformers(transformer)
            if "power_lines" in values.keys() and values["power_lines"] is not None:
                powerlines = values["power_lines"]
                #linecodes = values["linecode"]
                factory.gridController.setPowerLines(id, powerlines, linecodes)
            """and "linecode" in values.keys() and values["linecode"] is not None:"""

            if "photovoltaics" in values.keys() and values["photovoltaics"] is not None:
                photovoltaics = values["photovoltaics"]
                # xycurves = radial["xycurves"]
                # loadshapes = radial["loadshapes"]
                # tshapes = radial["tshapes"]
                factory.gridController.setPhotovoltaic(id, photovoltaics, xycurves, loadshapes, tshapes)

            """
            and "xycurves" in radial.values.keys()s() and radial["xycurves"] is not None 
                            and "loadshapes" in radial.values.keys()s() and radial["loadshapes"] is not None 
                            and "tshapes" in radial.values.keys()s() and radial["tshapes"] is not None: 
            """
            if "storage_units" in values.keys() and values["storage_units"] is not None:
                # radial=radial.to_dict()
                storage = values["storage_units"]
                factory.gridController.setStorage(id, storage)
            """if "chargingPoints" in values.keys() and values["chargingPoints"] is not None:
                # radial=radial.to_dict()
                chargingPoints = values["chargingPoints"]
                gridController.setChargingPoints(id, chargingPoints)
            """
                
                
            


        ######Disables circuits untilo the run simulation is started
        factory.gridController.disableCircuit(id)
        return str(id)
    else:
        return "Bad JSON Format"


def delete_simulation(id):  # noqa: E501
    """Delete a simulation and its data

     # noqa: E501

    :param id: ID of the simulation
    :type id: str

    :rtype: None
    """
    return 'do some magic!'


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
    return 'do some magic!'
