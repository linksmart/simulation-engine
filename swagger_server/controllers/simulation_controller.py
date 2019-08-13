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
        """redis_db = RedisDB()
        redis_db.set(id, "created")
        flag = redis_db.get(id)
        logger.debug("id stored in RedisDB: "+str(flag))"""
        #----------Profiles---------------#
        prof = Profiles()
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
            #dir_data = os.path.join(os.getcwd(), "optimization", str(id), "mqtt")
            #if not os.path.exists(dir_data):
                #os.makedirs(dir_data)
            if not os.path.exists("data"):
                os.makedirs("data")
            os.chdir(r"./data")
            fname = str(id)+"_input_grid"
            logger.debug("File name = " + str(fname))
            f = open(fname,'w')
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.close()
            os.chdir(r"../")
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
        common = grid.common.to_dict()
        factory.gridController.setNewCircuit(id, common)

        #factory.gridController.setLoadshape(id, npts, interval, mult)
        #factory.gridController.setLoadshape("test_loadschape", 8760, 1, load_profile_data)

        #factory.gridController.setNewCircuit(id)



        #----------PROFESS----------------#
        domain = factory.gridController.get_profess_url()+"/v1/"
        logger.debug("profess url: "+str(domain))
        profess = Profess(domain)
        #profess.json_parser.set_topology(data)




        profess.json_parser.set_topology(data)


        # ToDo  change sim_days
        sim_days = 365

        """
        dummyprofile = [3] * 24
        dummyLoads = []
        dummyPrice = []
        dummyPV = []
        
        
        dummyPVdict = []
        print("profess.json_parser.get_node_name_list(): " + str(profess.json_parser.get_node_name_list()))
        
        for element in profess.json_parser.get_node_name_list():
            print("element: " + str(element))
            dummyDict = { element: {element + ".1": copy.deepcopy(dummyprofile), element + ".2": copy.deepcopy(dummyprofile), element + ".3": copy.deepcopy(dummyprofile)}}
            print("dummyDict: " + str(dummyDict))
            dummyLoads.append(dummyDict)
            dummyPVdict = {element: {element + ".1.2.3": copy.deepcopy(dummyprofile)}}
            dummyPV.append(dummyPVdict)


        dummyPrice = copy.deepcopy(dummyprofile)
        
        element = "671"
        dummyDict = {element: [{element + ".1.2.3": copy.deepcopy(dummyprofile)}]}

        print("dummyDict: " + str(dummyDict))
        print("dummyLoads: " + str(dummyLoads))
        print("dummyPV: " +  str(dummyPV))
        print("dummyPrice: " + str(dummyPrice))

        print("dummyLoads len: " + str(len(dummyLoads)))

        dummyLoads[0] = dummyDict
        dummyGESSCON = [{'633': {'633.1.2.3': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]}},
                        {'671': {'671.1.2.3': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]}}]

        #profess.set_up_profess_for_existing_topology( dummyLoads, dummyPV, dummyPrice, dummyGESSCON)
        #profess.start_all()
        print(profess.dataList)
        print(profess.wait_and_get_output())

        soc_list = [{"633": {"SoC": 0.5}}, {"671": {"SoC": 0.4}}, {"634": {"SoC": 0.2}}]
        #profess.update(dummyLoads, dummyPV, dummyPrice, soc_list, dummyGESSCON)
        #print(profess.dataList)
        #---------------PROFESS_END--------------------#

        """
            
        for values in radial:
            #logger.debug("values of the radial: "+str(values))
            values=values.to_dict()
            #logger.debug("Values: "+str(values))


            if "transformer" in values.keys() and values["transformer"] is not None:
                #logger.debug("!---------------Setting Transformers------------------------")
                print("!---------------Setting Transformers------------------------ \n")
                transformer = values["transformer"]
#                logger.debug("Transformers" + str(transformer))
                factory.gridController.setTransformers(id,transformer)

            if "regcontrol" in values.keys() and values["regcontrol"] is not None:
#                logger.debug("---------------Setting RegControl------------------------")
                print("!---------------Setting RegControl------------------------ \n")
                regcontrol = values["regcontrol"]
#                logger.debug("RegControl" + str(regcontrol))
                factory.gridController.setRegControls(id, regcontrol)

            if "linecode" in values.keys() and values["linecode"] is not None:
                #logger.debug("---------------Setting LineCode-------------------------")
                print("! ---------------Setting LineCode------------------------- \n")
                linecode = values["linecode"]
                # logger.debug("LineCode: " + str(linecode))
                factory.gridController.setLineCodes(id, linecode)

            if "loads" in values.keys() and values["loads"] is not None:
                #logger.debug("---------------Setting Loads-------------------------")
                print("! ---------------Setting Loads------------------------- \n")
                # radial=radial.to_dict()
                load = values["loads"]
                # logger.debug("Loads" + str(load))
                print("! >>>  ---------------Loading Load Profiles beforehand ------------------------- \n")
                factory.gridController.setLoadshapes(id, load, sim_days, prof, profess)
                print("! >>>  ---------------and the Loads afterwards ------------------------- \n")
                factory.gridController.setLoads(id, load)

            if "capacitor" in values.keys() and values["capacitor"] is not None:
                #logger.debug("---------------Setting Capacitors-------------------------")
                print("! ---------------Setting Capacitors------------------------- \p")
                capacitor = values["capacitor"]
                # logger.debug("Capacitors: " + str(capacitor))
                factory.gridController.setCapacitors(id, capacitor)

            if "power_lines" in values.keys() and values["power_lines"] is not None:
                #logger.debug("---------------Setting Powerlines-------------------------")
                print("!---------------Setting Powerlines------------------------- \n")
                try:
                    powerLines = values["power_lines"]
                    #linecodes = values["linecode"]
                    #factory.gridController.setPowerLines(id, powerLines, linecodes) #TODO: Where does linecodes come from?
                    #logger.debug("Powerlines" + str(powerLines))
                    factory.gridController.setPowerLines(id, powerLines)
                except ValueError as e:
                    logger.error(e)

            if "powerProfile" in values.keys() and values["powerProfile"] is not None:
#                logger.debug("---------------Setting powerProfile-------------------------")
                print("!---------------Setting powerProfile------------------------- \n")
                powerProfile = values["powerProfile"]
                #logger.debug("Powerprofile" + str(powerProfile))
                factory.gridController.setPowerProfile(id, powerProfile)

            if "xycurves" in values.keys() and values["xycurves"] is not None:
                xycurves = values["xycurves"]#TORemove
                factory.gridController.setXYCurve(id, xycurves) 

            """if "photovoltaics" in values.keys() and values["photovoltaics"] is not None:
                photovoltaics = values["photovoltaics"]
                #xycurves = radial["xycurves"]
                #loadshapes = radial["loadshapes"]
                #tshapes = radial["tshapes"]
                factory.gridController.setPhotovoltaic(id, photovoltaics)""" #TODO: fix and remove comment

            """
            and "xycurves" in radial.values.keys()s() and radial["xycurves"] is not None 
                            and "loadshapes" in radial.values.keys()s() and radial["loadshapes"] is not None 
                            and "tshapes" in radial.values.keys()s() and radial["tshapes"] is not None: 
            """
            if "storage_units" in values.keys() and values["storage_units"] is not None:
                #logger.debug("---------------Setting Storage-------------------------")
                print("! ---------------Setting Storage------------------------- \n")
                # radial=radial.to_dict()
                storage = values["storage_units"]
                factory.gridController.setStorage(id, storage) #TODO: fix and remove comment

            """if "chargingPoints" in values.keys() and values["chargingPoints"] is not None:
                # radial=radial.to_dict()
                chargingPoints = values["chargingPoints"]
                gridController.setChargingPoints(id, chargingPoints)
            """
            if "chargingPoints" in values.keys() and values["chargingPoints"] is not None:
                #logger.debug("---------------Setting chargingPoints-------------------------")
                chargingPoints = values["chargingPoints"]
                factory.gridController.setChargingPoints(id, chargingPoints)               


            """if "voltage_regulator" in values.keys() and values["voltage_regulator"] is not None:
                logger.debug("---------------Setting Voltage regulator-------------------------")
                voltage_regulator = values["voltage_regulator"]
                logger.debug("Voltage Regulator: " + str(voltage_regulator))
                factory.gridController.setVoltageRegulator(id, voltage_regulator)
            """

            if "loadshapes" in values.keys() and values["loadshapes"] is not None:
#                logger.debug("---------------Setting loadshapes-------------------------")
                print("! ---------------Setting loadshapes------------------------- \n")
                loadshapes = values["loadshapes"]
#                logger.debug("Load Shapes: " + str(loadshapes))
                factory.gridController.setLoadShape(id, loadshapes)
            if "tshapes" in values.keys() and values["tshapes"] is not None:
                logger.debug("---------------Setting tshapes-------------------------")
                tshapes = values["tshapes"]
                logger.debug("Tshapes: " + str(tshapes))
                factory.gridController.setTShape(id, tshapes)      
            if "photovoltaics" in values.keys() and values["photovoltaics"] is not None:
                print("! ---------------Setting Photovoltaic------------------------- \n")
                photovoltaics = values["photovoltaics"]
                #xycurves = radial["xycurves"]
                #loadshapes = radial["loadshapes"]
                #tshapes = radial["tshapes"]

                city= factory.gridController.get_city()
                logger.debug("city "+str(city))
                country = factory.gridController.get_country()
                logger.debug("country "+str(country))
                if not city == None and not country == None:
                    print("! >>>  ---------------Loading PV Profiles beforehand ------------------------- \n")
                    factory.gridController.setPVshapes(id, photovoltaics, city, country, sim_days, prof, profess)
                    print("! >>>  ---------------and the PVs afterwards ------------------------- \n")
                    factory.gridController.setPhotovoltaic(id, photovoltaics)
                else:
                    logger.error("Fatal error: city and country are missing")
                print("! >>>  ---------------PVs finished ------------------------- \n")

        ######Disables circuits untilo the run simulation is started
        #factory.gridController.disableCircuit(id)
        topology=profess.json_parser.get_topology()
        result = factory.gridController.run(topology)
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
    #logger.info("Get Error")
    try:
        os.chdir(r"./data")
        f = open(str(id)+"_result") #open(str(id)+"_results.txt")
        #logger.debug("GET file "+str(f))
        content = f.read()
        #logger.info(content)
        result = json.loads(content)
        f.close()
        os.chdir(r"../")
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
